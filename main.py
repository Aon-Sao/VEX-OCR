from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from JobSpec import JobSpec
from Settings import Settings
from video_copy_manager import VideoCopyManager

settings: Settings = None
video_copy_manager: VideoCopyManager = None
log: structlog.BoundLogger = None


def setup_logging():
    global log
    structlog.configure(processors=[
        # structlog.processors.TimeStamper,
        # structlog.processors.dict_tracebacks,
        structlog.dev.ConsoleRenderer()
    ])
    log = structlog.get_logger()
    log.debug(f"Logging configured.")
    return log


def setup_env_vars():
    global settings
    log.debug("Loading .env")
    try:
        settings = Settings()
        return settings
    except Exception as e:
        log.critical("Exception while loading .env", exc_info=e)
        raise e


def setup_job_managers():
    global video_copy_manager
    log.debug(f"Creating VideoCopyManager instance")
    video_copy_manager = VideoCopyManager(settings)


def cleanup_job_managers():
    log.info(f"Shutting down executors")
    video_copy_manager.executor.shutdown(wait=True)
    video_copy_manager.ocr_manager.executor.shutdown(wait=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    setup_env_vars()
    setup_job_managers()

    log.debug(f"Lifespan yielding control")

    yield

    log.debug(f"Lifespan received control")

    cleanup_job_managers()


app = FastAPI(lifespan=lifespan)


@app.post("/create_job")
async def create_job(job_spec: JobSpec):
    log.info("Received job", endpoint="/create_job", job=job_spec.model_dump())
    video_copy_manager.add_job(job_spec).result()
    return


@app.post("/create_batch_job")
async def create_batch_job(job_spec_list: list[JobSpec]):
    log.info(f"Received batch job", endpoint="/create_batch_job",
             job_list={str(i.video_id): i.model_dump() for i in job_spec_list})
    for j in job_spec_list:
        await create_job(j)
    return
