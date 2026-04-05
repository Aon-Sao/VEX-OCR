import logging
import sys
from contextlib import asynccontextmanager
from logging import Logger
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from JobSpec import JobSpec
from video_copy_manager import VideoCopyManager

video_copy_manager: VideoCopyManager = None
log: Logger = None


def setup_logging():
    log_path = Path("logging-from-space.log")

    file_handler = logging.FileHandler(log_path)
    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[file_handler, console_handler],
    )

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical(
            f"Uncaught exception ", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception


@asynccontextmanager
async def lifespan(app: FastAPI):
    global log
    global video_copy_manager

    setup_logging()
    log = logging.getLogger(__name__)

    log.debug("Loading .env")
    load_dotenv()

    video_copy_manager = VideoCopyManager()

    yield

    video_copy_manager.executor.shutdown(wait=True)
    video_copy_manager.ocr_manager.executor.shutdown(wait=True)


app = FastAPI(lifespan=lifespan)


@app.post("/create_job")
async def create_job(job_spec: JobSpec):
    video_copy_manager.add_job(job_spec).result()
    return


@app.post("/create_batch_job")
async def create_batch_job(job_spec_list: list[JobSpec]):
    for j in job_spec_list:
        await create_job(j)
    return
