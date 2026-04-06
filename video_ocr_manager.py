import json
import pathlib
import threading
from concurrent.futures import ProcessPoolExecutor

import structlog

from JobSpec import JobSpec
from Settings import Settings
from ocr import run_ocr


class VideoOCRManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VideoOCRManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, settings: Settings):
        self.log = structlog.get_logger()
        if self._initialized:
            return
        self.log.debug("Creating ProcessPoolExecutor")
        self.executor = ProcessPoolExecutor(
            max_workers=settings.max_workers, max_tasks_per_child=1
        )
        self.pg_conn_str = settings.postgres_connection_string
        self.worker_host = settings.worker_host

        self._initialized = True

    def process_video(self, video_data: JobSpec, tmp_path: pathlib.Path):
        try:
            json_dict = {
                "pg_conn_str": str(self.pg_conn_str),
                "ssd_vid_path": tmp_path.as_posix(),
                "scan_start_offset": video_data.scan_start_offset,
                "divisions": [i.model_dump() for i in video_data.divisions],
                "video_id": video_data.video_id,
                "worker_host": self.worker_host,
                "ocr_regions": {
                    "MATCH_NUM": [0, 0, 420, 56],
                    "DIVISION_NAME": [423, 0, 1499, 53],
                    "MATCH_TIMER": [1654, 944, 1920, 1043],
                    "MATCH_MODE": [1654, 1044, 1920, 1080],
                },
            }
            json_str = json.dumps(json_dict)
        except Exception as e:
            self.log.critical("Exception while constructing json for OCR tool", exc_info=e)
        future = self.executor.submit(run_ocr, json_str, video_data.video_id)
        self.log.info("Job submitted", job=video_data)
        return future
