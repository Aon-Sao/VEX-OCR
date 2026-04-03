import os
import cv2
from pathlib import Path
from subprocess import run, CalledProcessError

from ocr.DataObjects import InputData
from ocr.FileBrowser import FileBrowser


class Config:
    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
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
            "MATCH_MODE": None
        }

        # Seconds between auton and driver
        self.max_phase_distance = 5 * 60
        # How many frames should be quality checked within a phase
        self.num_phase_quality_checks = 5

        self.expected_strings = [
            "HS",
            "MS",
            "ES",
            "High",
            "Middle",
            "Elementary",
            "School",
            "Qual", "Qualification", "Qualifications",
            "Practice",
            "QF", "Quarterfinal", "Quarter-final",
            "SF", "Semifinal", "Semi-final",
            "F", "Final",
            "R16", "Round of 16", "Round-of-16",
            "R32", "Round of 16", "Round-of-32",
            "R64", "Round of 16", "Round-of-64",
            "R128", "Round of 16", "Round-of-128",
            "Skills",
            "Timeout",
            "Top",
            "Driver", "Driver Control",
            "Auton", "Autonomous",
            "Control",
        ]

    def configure(self, input_data: InputData):
        self.scan_start_offset = input_data.scan_start_offset
        self.pg_conn_str = input_data.pg_conn_str
        self.divisions = input_data.divisions
        self.video_id = input_data.video_id
        self.video_path = Path(input_data.ssd_vid_path)
        self.set_fps_and_total_frames()
        self.worker_host = input_data.worker_host
        self.division_names = [i.division_name for i in self.divisions]
        self.driver_skip_size, self.auton_skip_size = self.set_skip_sizes()
        self.expected_strings.extend(self.division_names)
        self.expected_strings.extend({i.program_code for i in self.divisions})
        self.expected_strings = [i.lower() for i in self.expected_strings]

        for k in self.ocr_regions.keys():
            self.ocr_regions[k] = getattr(input_data.ocr_regions, k)

    def open_video(self):
        self.video_obj = cv2.VideoCapture(self.video_path)

    def release_video(self):
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
        args = ["ffprobe", "-v", "er"
                                 "ror", "-select_streams", "v:0", "-count_packets", "-of",
                "default=noprint_wrappers=1:nokey=1",
                "-show_entries", "stream=avg_frame_rate,nb_read_packets", str(self.video_path.absolute())]
        try:
            proc = run(args=args, capture_output=True, check=True)
        except CalledProcessError as e:
            raise Exception(e.stderr.decode())
        output = proc.stdout.decode()
        fps_str, total_frames = output.split("\n", maxsplit=1)
        n, d = fps_str.split(r"/")
        self.fps = float(n) / float(d)
        self.frame_count = int(total_frames)


CONFIG = Config()
