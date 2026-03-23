import pathlib
import shutil
import os
import threading
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

from video_ocr_manager import VideoOCRManager


class VideoCopyManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VideoCopyManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, tmp_dir=os.environ["TMP_DIR"], threshold_gb=float(os.environ["THRESHOLD_GB"]),
                 max_queued_files=int(os.environ["MAX_WORKERS"]) * 3, max_workers=int(os.environ["MAX_WORKERS"]),
                 cleanup_tmp=bool(os.environ["CLEANUP_TMP"] == "TRUE"),
                 skip_copy_if_exists=bool(os.environ["SKIP_COPY_IF_EXISTS"] == "TRUE")):
        if self._initialized: return
        self.tmp_root = pathlib.Path(tmp_dir)
        self.ensure_tmp_dir()
        self.threshold_gb = threshold_gb
        self.cleanup_tmp = cleanup_tmp
        self.skip_copy_if_exists = skip_copy_if_exists
        self.ocr_manager = VideoOCRManager(max_workers)
        self.transfer_semaphore = threading.Semaphore(max_queued_files)
        self.space_ready_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._initialized = True

    def add_job(self, video_data):
        future = self.executor.submit(self._worker_loop, video_data)
        print(f"[VIDEO_COPY_MANAGER] Job submitted {video_data['video_id']}]")
        return future

    def trigger_check(self):
        self.space_ready_event.set()

    def _get_free_space_gb(self):
        self.ensure_tmp_dir()
        space = shutil.disk_usage(self.tmp_root).free / (1024 ** 3)
        return space

    def _cleanup_after_ocr(self, tmp_path: pathlib.Path):
        try:
            if self.cleanup_tmp:
                tmp_path.unlink(missing_ok=True)
                print(f"[Cleanup] Deleted {tmp_path}")
            else:
                print(f"[Cleanup] Skipped deleting {tmp_path}")

        finally:
            self.transfer_semaphore.release()
            self.trigger_check()

    def _worker_loop(self, video_data):
        self.transfer_semaphore.acquire()

        src_path = pathlib.Path(video_data["network_path"])
        file_name = src_path.name
        dst_path = self.tmp_root / file_name
        self.ensure_tmp_dir()
        print(f"[Transfer] Copying {file_name} from {src_path} to {dst_path}")

        if dst_path.exists() and self.skip_copy_if_exists:
            print(f"[Transfer] File already existed {dst_path}")

        else:
            while self._get_free_space_gb() < self.threshold_gb:
                print(f"[Wait] Low space for {file_name}. Waiting...")
                self.space_ready_event.wait(timeout=30)
            self.space_ready_event.clear()

            shutil.copy2(src_path, dst_path)
            sleep(10)

        future = self.ocr_manager.process_video(video_data, dst_path)

        def clean(f):
            f.result()
            sleep(10)
            self._cleanup_after_ocr(dst_path)

        future.add_done_callback(clean)

    def ensure_tmp_dir(self):
        self.tmp_root.mkdir(parents=True, exist_ok=True)
