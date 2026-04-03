import os
import threading
from pathlib import Path
from threading import Semaphore, Condition

# from contextlib import asynccontextmanager
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from VideoCopyJob import VideoCopyJob
from VideoOCRJob import VideoOCRJob


scheduler: BackgroundScheduler = None
copy_semaphore: Semaphore = None
disk_space_cond: Condition = None


def start_scheduler():
    global scheduler, copy_semaphore, disk_space_cond
    load_dotenv()
    max_workers = int(os.environ["MAX_WORKERS"])
    max_queued_files = max_workers * 3
    copy_semaphore = threading.Semaphore(max_queued_files)
    disk_space_cond = threading.Condition()

    executors = {
        "threadpool": ThreadPoolExecutor(max_workers=1),
        "processpool": ProcessPoolExecutor(max_workers=max_workers)
    }
    scheduler = BackgroundScheduler(executors=executors)
    scheduler.start()
    return scheduler, copy_semaphore, disk_space_cond

class JobJson(BaseModel):
    class Division(BaseModel):
        event_sku: str
        program_code: str
        division_name: str
    src_file: str
    dst_dir: str
    src_file_hash: str | None = None
    src_file_size: int | None = None
    video_id: int
    divisions: list[Division]
    scan_start_offset: int = 0

def copy_task(job_json: JobJson):
    print(f"Starting copy for vid_id: {job_json.video_id}")
    copy_job_result = VideoCopyJob(
        src_file=Path(job_json.src_file),
        dst_dir=Path(job_json.dst_dir),
        src_file_size=job_json.src_file_size,
        disk_buffer_size=0,  # TODO: load from .env
        vid_id=job_json.video_id,
        semaphore=copy_semaphore,
        cond=disk_space_cond,
        src_file_hash=job_json.src_file_hash
    ).perform()
    scheduler.add_job(func=ocr_task, args=[job_json], executor="processpool")
    return copy_job_result

def ocr_task(job_json: JobJson):
    print(f"Starting OCR for vid_id: {job_json.video_id}")
    ocr_job_result = VideoOCRJob(
        video_path=Path(job_json.dst_dir) / Path(job_json.src_file).name,
        scan_start_offset=job_json.scan_start_offset,
        divisions=[div.model_dump() for div in job_json.divisions],
        video_id=job_json.video_id
    ).perform()
    scheduler.add_job(func=cleanup_task, args=[job_json], executor="threadpool")
    return ocr_job_result

def cleanup_task(job_json: JobJson):
    print(f"Starting cleanup for vid_id: {job_json.video_id}")
    cleanup_result = VideoCopyJob.clean_up_file(Path(job_json.dst_dir) / Path(job_json.src_file).name)
    print(f"Cleanup done for vid_id: {job_json.video_id}")
    scheduler.add_job(func=report_completion, args=[job_json], executor="threadpool")
    return cleanup_result

def report_completion(job_json: JobJson):
    # In the future, emit HTTP
    print(f"COMPLETE: vid_id: {job_json.video_id}")

def schedule_job(job_json: JobJson):
    scheduler.add_job(func=copy_task, args=[job_json], executor="threadpool")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     start_scheduler()
#     yield

# Python will wait until start_scheduler returns before creating the FastAPI app
start_scheduler()
app = FastAPI()

@app.post("/create_job")
def create_job(job_json: JobJson):
    schedule_job(job_json=job_json)
    return
