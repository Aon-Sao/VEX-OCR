import os
import cv2
from pathlib import Path
from subprocess import run

from ocr.DataObjects import InputData
from ocr.FileBrowser import FileBrowser


class Config:
    # Affects how big a skip we'll take
    # We want to guarantee 2 or 3 hits in a phase
    def make_skip_size(self, phase_duration):
        return int((phase_duration / 3) * self.fps)

    ocr_regions = {
        "MATCH_NUM": None,
        "DIVISION_NAME": None,
        "MATCH_TIMER": None,
        "MATCH_MODE": None
    }
    # Seconds between auton and driver
    max_phase_distance = 5 * 60
    tesseract_path = "/usr/sbin/tesseract"
    expected_strings = [
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

    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def configure(self, input_data: InputData):
        self.scan_start_offset = input_data.scan_start_offset
        self.pg_conn_str = input_data.pg_conn_str
        self.set_video_path(input_data.ssd_vid_path)
        self.divisions = input_data.divisions
        self.division_names = [i.division_name for i in self.divisions]
        self.expected_strings.extend(self.division_names)
        self.expected_strings.extend({i.program_code for i in self.divisions})
        self.expected_strings = [i.lower() for i in self.expected_strings]
        self.driver_skip_size, self.auton_skip_size = self.get_skip_sizes()
        self.video_id = input_data.video_id
        self.worker_host = input_data.worker_host

        for k in self.ocr_regions.keys():
            self.ocr_regions[k] = getattr(input_data.ocr_regions, k)
    def release(self):
        self.video_obj.release()

    def get_skip_sizes(self):
        shortest_driver = min([dv.driver_duration for dv in self.divisions])
        shortest_auton = min([dv.auton_duration for dv in self.divisions])
        return self.make_skip_size(shortest_driver), self.make_skip_size(shortest_auton)

    def set_video_path(self, vid_path):
        self.video_path = Path(vid_path)
        self.video_obj = cv2.VideoCapture(self.video_path)
        self.set_fps_and_total_frames()

    def set_fps_and_total_frames(self):
        try:
            args = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    "-show_entries", "stream=avg_frame_rate,nb_read_packets", str(self.video_path.absolute())]
            proc = run(args=args, capture_output=True)
            output = proc.stdout.decode()
            fps_str, total_frames = output.split("\n", maxsplit=1)
            n, d = fps_str.split(r"/")
            self.fps = float(n) / float(d)
            self.frame_count = int(total_frames)
        except Exception as e:
            print(e)

    def select_ocr_regions(self, time):
        for region in self.ocr_regions.keys():
            if self.ocr_regions[region] is None:
                self.select_ocr_region(time, region)

    def select_ocr_region(self, time, field_type):
        frame_num = int(float(time) * self.fps)
        self.video_obj.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.video_obj.read()
        title = f"Select {field_type}"
        sel = self.select_region(frame, title)
        self.ocr_regions[field_type] = list(sel)

    @staticmethod
    def select_region(img, title="Select region"):
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        print(title)
        top_left_x, top_left_y, width, height = cv2.selectROI(windowName=title, img=img)
        bottom_right_x = top_left_x + width
        bottom_right_y = top_left_y + height
        cv2.destroyWindow(winname=title)
        return top_left_x, top_left_y, bottom_right_x, bottom_right_y

    def select_video_path(self):
        self.set_video_path(FileBrowser("Select video file", os.getcwd()).browse())


CONFIG = Config()
