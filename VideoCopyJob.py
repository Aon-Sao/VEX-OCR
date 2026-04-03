import hashlib
import logging
import shutil
from pathlib import Path
from threading import Condition, Semaphore

from Monitors import Units

log = logging.getLogger(__name__)

class InsufficientDiskSpace(OSError):
    pass


class VideoCopyJob:

    def __init__(self, src_file: Path, dst_dir: Path, src_file_size: int, disk_buffer_size: int, vid_id: int,
                 semaphore: Semaphore, cond: Condition, src_file_hash: str | None = None):
        self.src_file = Path(src_file)
        self.dst_dir = Path(dst_dir)
        self.dst_file = self.dst_dir / self.src_file.name
        self.src_file_hash = src_file_hash
        self.src_file_size = src_file_size
        self.disk_buffer_size = disk_buffer_size
        self.vid_id = vid_id
        self.semaphore = semaphore
        self.disk_space_cond = cond

    def perform(self):
        log.debug(f"Obtaining disk_space condition lock for vid_id: {self.vid_id}")
        with self.disk_space_cond:
            log.debug(f"Waiting for disk_space condition predicate for vid_id: {self.vid_id}")
            self.disk_space_cond.wait_for(lambda : self.disk_has_room(self.src_file_size, Path(self.dst_dir.drive), self.disk_buffer_size))
            log.debug(f"disk_space wait complete for vid_id: {self.vid_id}")
        log.debug(f"Releasing disk_space condition lock for vid_id: {self.vid_id}")
        success, attempted_copy, need_to_copy = None, None, None
        success, need_to_copy = self.examine_disk()
        while need_to_copy and (not attempted_copy):
            attempted_copy, _ = self.copy_files()
            success, need_to_copy = self.examine_disk()
        log.debug(f"Finished copy job for vid_id: {self.vid_id}")
        return success

    def examine_disk(self):
        log.debug(f"Examining disk for vid_id: {self.vid_id}")
        src_exists = VideoCopyJob.path_exists(self.src_file)
        dst_file_exists = VideoCopyJob.path_exists(self.dst_file)
        self.dst_dir.mkdir(exist_ok=True)

        if not src_exists:
            raise FileNotFoundError(f"Cannot copy, video file does not exist: {self.src_file}")

        if dst_file_exists:
            if VideoCopyJob.files_match(self.src_file, self.dst_file, self.src_file_hash):
                success = True
                need_to_copy = False
                log.debug(f"File already exists and matches, no need to copy for vid_id: {self.vid_id}")
                return success, need_to_copy

        if not self.disk_has_room(self.src_file_size, self.dst_dir, self.disk_buffer_size):
            return InsufficientDiskSpace(f"Not enough room on disk for {self.src_file}")

        success = False
        need_to_copy = True
        log.debug(f"File does not exist or does not match, time to copy for vid_id: {self.vid_id}")
        return success, need_to_copy

    def copy_files(self):
        log.debug(f"Obtaining copy_semaphore for vid_id: {self.vid_id}")
        with self.semaphore:
            attempted_copy = True
            log.debug(f"Starting copy for vid_id: {self.vid_id}")
            a, b = attempted_copy, shutil.copy2(self.src_file, self.dst_dir)
            log.debug(f"Finished copy for vid_id: {self.vid_id}")
        log.debug(f"Releasing copy_semaphore for vid_id: {self.vid_id}")
        return a, b

    @staticmethod
    def free_space(dst_dir: Path):
        # In bytes
        return shutil.disk_usage(dst_dir).free

    @staticmethod
    def disk_has_room(src_size: int, dst_dir: Path, buffer_size: int):
        room_remaining = VideoCopyJob.free_space(dst_dir) - src_size
        enough_space = room_remaining >= buffer_size
        return enough_space

    @staticmethod
    def path_exists(fpath: Path) -> bool:
        return fpath.exists()

    @staticmethod
    def files_match(src_file, dst_file, src_file_hash) -> bool:
        if src_file_hash is None:
            hash_match = True
        else:
            hash_match = src_file_hash == VideoCopyJob.hash_file(dst_file)
        return (src_file.name == dst_file.name) and hash_match

    @staticmethod
    def hash_file(fpath: Path) -> str:
        buf_size = 65 * Units.KB  # Saw someone else pick this value
        sha256 = hashlib.sha256()
        with open(fpath, 'rb') as fin:
            while data := fin.read(buf_size):
                sha256.update(data)
        return sha256.hexdigest()

    @staticmethod
    def clean_up_file(fpath: Path):
        fpath.unlink(missing_ok=True)
