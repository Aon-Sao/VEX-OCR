import os
import threading
from time import sleep

from dotenv import load_dotenv
from pubsub import pub
from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

load_dotenv()
max_workers = int(os.environ["MAX_WORKERS"])
max_queued_files = max_workers * 3
semaphore = threading.Semaphore(max_queued_files)
disk_space_cond = threading.Condition()

executors = {
    "threadpool": ThreadPoolExecutor(),
    "processpool": ProcessPoolExecutor()
}
scheduler = BackgroundScheduler(executors=executors)
scheduler.start()

class JobJson(BaseModel):
    class Division(BaseModel):
        event_sku: str
        program_code: str
        division_name: str
    src_file: str
    dst_dir: str
    src_file_hash: str = None
    src_file_size: int
    video_id: int
    divisions: list[Division]

def fake_copy_task(job_json: JobJson):
    def disk_has_room():
        sleep(1)
        return True
    print(f"Start copy task for vid_id: {job_json.video_id}")
    with disk_space_cond:
        print(f"Waiting for disk space for vid_id: {job_json.video_id}")
        disk_space_cond.wait_for(disk_has_room)
    with semaphore:
        print(f"Doing copy for vid_id: {job_json.video_id}")
        sleep(2)
    print(f"Copy done for vid_id: {job_json.video_id}")
    scheduler.add_job(func=fake_ocr_task, args=[job_json], executor="processpool")

def fake_ocr_task(job_json: JobJson):
    print(f"Starting OCR for vid_id: {job_json.video_id}")
    sleep(3)
    print(f"OCR done for vid_id: {job_json.video_id}")
    scheduler.add_job(func=fake_cleanup_task, args=[job_json], executor="threadpool")

def fake_cleanup_task(job_json: JobJson):
    print(f"Starting cleanup for vid_id: {job_json.video_id}")
    sleep(3)
    print(f"Cleanup done for vid_id: {job_json.video_id}")

def schedule_job(job_json: JobJson):
    scheduler.add_job(func=fake_copy_task, args=[job_json], executor="threadpool")

pub.subscribe(schedule_job, "job_creation")

app = FastAPI()

@app.post("/create_job")
def create_job(job_json: JobJson):
    pub.sendMessage("job_creation", job_json=job_json)
    return
