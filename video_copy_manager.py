import pathlib
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from time import sleep

import structlog

from JobSpec import JobSpec
from Settings import Settings
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

    def __init__(
        self,
        settings: Settings,
        tmp_dir=None,
        threshold_gb=None,
        max_queued_files=None,
        max_workers=None,
        cleanup_tmp=None,
        skip_copy_if_exists=None,
    ):
        if self._initialized:
            return

        self.log = structlog.get_logger()

        # Defaults
        self.tmp_dir = settings.tmp_dir if tmp_dir is None else tmp_dir
        self.threshold_gb = settings.threshold_gb if threshold_gb is None else threshold_gb
        self.cleanup_tmp = settings.cleanup_tmp if cleanup_tmp is None else cleanup_tmp
        self.skip_copy_if_exists = settings.skip_copy_if_exists if skip_copy_if_exists is None else skip_copy_if_exists

        max_workers = settings.max_workers if max_workers is None else max_workers
        max_queued_files = (3 * max_workers) if max_queued_files is None else max_queued_files

        self.transfer_semaphore = Semaphore(max_queued_files)
        self.log.debug("Creating ThreadPoolExecutor")
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.space_ready_event = threading.Event()
        self.log.debug("Creating VideoOCRManager")
        self.ocr_manager = VideoOCRManager(settings)
        self.ensure_tmp_dir()

        self._initialized = True

    def add_job(self, video_data: JobSpec):
        future = self.executor.submit(self._worker_loop, video_data)
        self.log.info("Job submitted", video_data=video_data)
        return future

    def trigger_check(self):
        self.space_ready_event.set()

    def _get_free_space_gb(self):
        self.ensure_tmp_dir()
        space = shutil.disk_usage(self.tmp_dir).free / (1024 ** 3)
        return space

    def _cleanup_after_ocr(
        self, video_data: JobSpec, dst_path: pathlib.Path, sleep_sec=60
    ):
        try:
            if self.cleanup_tmp and dst_path.exists():
                self.log.debug("Waiting before cleanup", video_id=video_data.video_id, dst_path=dst_path, sleep_sec=sleep_sec)
                sleep(sleep_sec)
                dst_path.unlink()
                self.log.debug("Deleted video", video_id=video_data.video_id, dst_path=dst_path)
            else:
                self.log.debug(f"Skipped deleting video", video_id=video_data.video_id, dst_path=dst_path)
        finally:
            self.transfer_semaphore.release()
            self.trigger_check()

    def _worker_loop(self, video_data: JobSpec):
        src_path = pathlib.Path(video_data.src_file)
        file_name = src_path.name
        dst_path = self.tmp_dir / file_name
        try:
            self.transfer_semaphore.acquire()

            self.ensure_tmp_dir()
            self.log.info("Copying file to %s", dst_path)

            if dst_path.exists() and self.skip_copy_if_exists:
                self.log.info("File already existed at %s", dst_path)
            else:
                while (s:=self._get_free_space_gb()) < self.threshold_gb:
                    self.log.info("Low disk space. Waiting...", disk_space=s)
                    self.space_ready_event.wait(timeout=30)
                self.space_ready_event.clear()

                shutil.copy2(src_path, dst_path)
                sleep(10)
        except Exception as e:
            self.log.critical("Exception while copying video file", exc_info=e)
        def clean(f):
            try:
                f.result()
                self._cleanup_after_ocr(video_data, dst_path)
            except Exception as ee:
                self.log.error("Exception while cleaning up video file", exc_info=ee)

        future = self.ocr_manager.process_video(video_data, dst_path)
        future.add_done_callback(clean)

    def ensure_tmp_dir(self):
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
