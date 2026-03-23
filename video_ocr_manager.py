import pathlib
import threading
import time
from concurrent.futures import ProcessPoolExecutor


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
        if self._initialized: return
        self.executor = ProcessPoolExecutor(max_workers=num_workers)
        self._initialized = True

    def process_video(self, video_data, tmp_path: pathlib.Path, on_complete_callback):
        json_str = ""
        future = self.executor.submit(self._ocr_logic, json_str)
        future.add_done_callback(lambda f: on_complete_callback(tmp_path))

    @staticmethod
    def _ocr_logic(json_str):
        """This runs in a separate Process."""
        # todo ocr worker call here
        return True
