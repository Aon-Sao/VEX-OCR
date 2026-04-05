import json
import os
import pathlib
import threading
import time
from concurrent.futures import ProcessPoolExecutor

from JobSpec import JobSpec
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

    def __init__(self, num_workers=4):
        if self._initialized:
            return
        self.executor = ProcessPoolExecutor(
            max_workers=num_workers, max_tasks_per_child=1
        )
        self._initialized = True

    def process_video(self, video_data: JobSpec, tmp_path: pathlib.Path):
        json_dict = {
            "pg_conn_str": os.environ["POSTGRES_CONNECTION_STRING"],
            "ssd_vid_path": tmp_path.as_posix(),
            "scan_start_offset": video_data.scan_start_offset,
            "divisions": [i.model_dump() for i in video_data.divisions],
            "video_id": video_data.video_id,
            "worker_host": os.environ["WORKER_HOST"],
            "ocr_regions": {
                "MATCH_NUM": [0, 0, 420, 56],
                "DIVISION_NAME": [423, 0, 1499, 53],
                "MATCH_TIMER": [1654, 944, 1920, 1043],
                "MATCH_MODE": [1654, 1044, 1920, 1080],
            },
        }
        json_str = json.dumps(json_dict)
        future = self.executor.submit(run_ocr, json_str, video_data.video_id)
        print(
            f"[VIDEO_OCR_MANAGER] Job submitted {video_data.video_id} json_str: {json_str}"
        )

        return future
