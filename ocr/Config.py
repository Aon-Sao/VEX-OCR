from pathlib import Path
from subprocess import run, CalledProcessError

import cv2
import structlog

from ocr.DataObjects import InputData


class Config:
    # Singleton
    instance = None
    log = structlog.get_logger()

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.input_data = None
        self.video_obj = None
        self.video_path = None
        self.frame_count = None
        self.fps = None
        self.worker_host = None
        self.video_id = None
        self.auton_skip_size = None
        self.driver_skip_size = None
        self.division_names = None
        self.divisions = None
        self.pg_conn_str = None
        self.scan_start_offset = 0
        self.ocr_regions = {
            "MATCH_NUM": None,
            "DIVISION_NAME": None,
            "MATCH_TIMER": None,
            "MATCH_MODE": None,
        }

        # Seconds between auton and driver
        self.max_phase_distance = 5 * 60
        # How many frames should be quality checked within a phase
        self.num_phase_quality_checks = 5

    def configure(self, input_data: InputData):
        self.log.debug("Configuring", input_data=input_data)
        self.input_data = input_data
        self.scan_start_offset = input_data.scan_start_offset
        self.pg_conn_str = input_data.pg_conn_str
        self.divisions = input_data.divisions
        self.video_id = input_data.video_id
        self.set_fps_and_total_frames()
        self.worker_host = input_data.worker_host
        self.division_names = [i.division_name for i in self.divisions]
        self.driver_skip_size, self.auton_skip_size = self.set_skip_sizes()

        for k in self.ocr_regions.keys():
            self.ocr_regions[k] = getattr(input_data.ocr_regions, k)

    def open_video(self):
        self.log.debug("Creating cv2 VideoCapture")
        self.video_obj = cv2.VideoCapture(Path(self.input_data.ssd_vid_path))

    def release_video(self):
        self.log.info("Releasing hardware & files")
        self.log.debug("Closing cv2 VideoCapture")
        self.video_obj.release()

    def set_skip_sizes(self):
        # Affects how big a skip we'll take
        # We want to guarantee 2 or 3 hits in a phase
        shortest_driver = min([dv.driver_duration for dv in self.divisions])
        shortest_auton = min([dv.auton_duration for dv in self.divisions])
        driver_skip_size = int((shortest_driver / 3) * self.fps)
        auton_skip_size = int((shortest_auton / 3) * self.fps)
        return driver_skip_size, auton_skip_size

    def set_fps_and_total_frames(self):
        args = [
            "ffprobe",
            "-v",
            "er" "ror",
            "-select_streams",
            "v:0",
            "-count_packets",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            "-show_entries",
            "stream=avg_frame_rate,nb_read_packets",
            str(Path(self.input_data.ssd_vid_path).absolute()),
        ]
        self.log.debug("Running ffprobe")
        try:
            proc = run(args=args, capture_output=True, check=True)
        except CalledProcessError as e:
            self.log.error("ffprobe failed", exc_info=e, stdout=e.stderr.decode())
            raise e
        output = proc.stdout.decode()
        fps_str, total_frames = output.split("\n", maxsplit=1)
        n, d = fps_str.split(r"/")
        self.fps = float(n) / float(d)
        self.frame_count = int(total_frames)


CONFIG = Config()
