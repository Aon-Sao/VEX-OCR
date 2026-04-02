import json
import logging
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

log = logging.getLogger(__name__)
from dotenv import load_dotenv

from ocr import run_ocr


class VideoOCRJob:

    load_dotenv()
    max_workers = int(os.environ["MAX_WORKERS"])
    executor = ProcessPoolExecutor(max_workers=max_workers, max_tasks_per_child=1)

    def __init__(self, video_path: Path, scan_start_offset: int,
                 divisions: list, video_id: int):
        self.video_path = Path(video_path)
        self.scan_start_offset = scan_start_offset
        self.divisions = divisions
        self.video_id = video_id
        self.pg_conn_str = os.environ["POSTGRES_CONNECTION_STRING"]
        self.worker_host = os.environ["WORKER_HOST"]
        self.ocr_job_json = None
        self.success = None

    def submit(self):
        return self.executor.submit(self.perform)

    def perform(self):
        self.make_ocr_job_json()
        self._run_ocr()
        log.debug(f"Finished ocr for vid_id: {self.video_id}")
        return self.success

    def _run_ocr(self):
        log.debug(f"Starting ocr script for vid_id: {self.video_id}")
        self.success = run_ocr(self.ocr_job_json, self.video_id)

    def make_ocr_job_json(self):
        log.debug(f"Making ocr json for vid_id: {self.video_id}")
        json_dict = {
            "pg_conn_str": self.pg_conn_str,
            "ssd_vid_path": self.video_path.as_posix(),
            "scan_start_offset": self.scan_start_offset,
            "divisions": self.divisions,
            "video_id": self.video_id,
            "worker_host": self.worker_host,
            "ocr_regions": {
                "MATCH_NUM": [
                    0,
                    0,
                    420,
                    56
                ],
                "DIVISION_NAME": [
                    423,
                    0,
                    1499,
                    53
                ],
                "MATCH_TIMER": [
                    1654,
                    944,
                    1920,
                    1043
                ],
                "MATCH_MODE": [
                    1654,
                    1044,
                    1920,
                    1080
                ]
            }
        }
        json_str = json.dumps(json_dict)
        self.ocr_job_json = json_str
        return self.ocr_job_json
