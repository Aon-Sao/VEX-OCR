from contextlib import asynccontextmanager

from fastapi import FastAPI

from JobSpec import JobSpec
from video_copy_manager import VideoCopyManager

video_copy_manager: VideoCopyManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global video_copy_manager
    video_copy_manager = VideoCopyManager()
    yield
    video_copy_manager.executor.shutdown(wait=True)
    video_copy_manager.ocr_manager.executor.shutdown(wait=True)


app = FastAPI(lifespan=lifespan)


@app.post("/create_job")
async def create_job(job_spec: JobSpec):
    video_copy_manager.add_job(job_spec).result()
    return
