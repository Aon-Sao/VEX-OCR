import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from VideoCopyJob import VideoCopyJob
from VideoOCRJob import VideoOCRJob

log = logging.getLogger(__name__)


def setup_logging():
    log_path = Path("logging-from-space.log")

    file_handler = logging.FileHandler(log_path)
    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[file_handler, console_handler]
    )

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical(f"Uncaught exception ", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def process_video(video_data, tmp_dir: Path, disk_buffer_size: int, cleanup_tmp: bool):
    remote_video_file = Path(video_data["network_path"])
    local_video_file = tmp_dir / remote_video_file.name
    vid_id = video_data["video_id"]

    futures = []

    log.info(f"Beginning to process vid_id: {vid_id}")

    def copy():
        ## COPY
        # Set up job
        log.debug(f"Setting up copy job for vid_id: {vid_id}")
        file_hash = video_data["file_hash"] if "file_hash" in video_data else None
        copy_job = VideoCopyJob(
            remote_video_file,
            tmp_dir,
            video_data["file_size"],
            disk_buffer_size,
            vid_id,
            file_hash,
        )
        # Submit job to copy_executor
        log.debug(f"Submitting copy job for vid_id: {vid_id}")
        copy_future = copy_job.submit()
        copy_future.add_done_callback(ocr)
        # log.debug(f"Waiting for copy job for vid_id: {vid_id}")
        # copy_future.result()
        futures.append(copy_future)
        return copy_future

    def ocr(_):
        ## OCR
        # Set up job
        log.debug(f"Setting up OCR job for vid_id: {vid_id}")
        ocr_job = VideoOCRJob(
            local_video_file,
            video_data["scan_start_offset"],
            video_data["divisions"],
            vid_id
        )
        # Submit job to ocr_executor
        log.debug(f"Submitting OCR job for vid_id: {vid_id}")
        ocr_future = ocr_job.submit()
        ocr_future.add_done_callback(clean)
        # log.debug(f"Waiting for OCR job for vid_id: {vid_id}")
        # ocr_future.result()
        futures.append(ocr_future)
        return ocr_future

    def clean(_):
        ## CLEAN
        if cleanup_tmp:
            log.debug(f"Starting clean for vid_id: {vid_id}")
            VideoCopyJob.clean_up_file(local_video_file)
            log.debug(f"Finished clean for vid_id: {vid_id}")
        return cleanup_tmp

    copy()
    return futures


async def main():
    # Setup
    setup_logging()
    log.debug("Logging configured. Parsing config.json")
    with open("config.json") as fin:
        config = json.load(fin)
    log.debug("Loading .env")
    load_dotenv()
    tmp_dir = Path(os.environ["TMP_DIR"])
    disk_buffer_size = int(os.environ["THRESHOLD_GB"])
    cleanup_tmp = os.environ["CLEANUP_TMP"] == "TRUE"

    futures = []

    videos = config["videos"]
    for v in videos:
        futures.extend(process_video(v, tmp_dir, disk_buffer_size, cleanup_tmp))

    for f in futures:
        f.result()


if __name__ == "__main__":
    asyncio.run(main())
