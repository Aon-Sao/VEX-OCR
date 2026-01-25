import os
from subprocess import run
import cv2
from FileBrowser import FileBrowser
from DataObjects import *

class Config:
    ocr_regions = {
        "MATCH_NUM": [0, 0, 0, 0],
        "DIVISION_NAME": [0, 0, 0, 0],
        "MATCH_TIMER": [0, 0, 0, 0],
        "MATCH_MODE": [0, 0, 0, 0],
    }
    # Affects how big a skip we'll take
    skip_lambda = lambda match_phase_duration: match_phase_duration / 3
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
    def __new__(cls, input_data: InputData):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, input_data: InputData):
        self.frame_count = None
        self.fps = None
        self.video_obj = None
        self.pg_conn_str = input_data.pg_conn_str
        self.set_video_path(input_data.ssd_vid_path)
        self.divisions = input_data.divisions
        for dv in self.divisions:
            self.expected_strings.append(dv.program_code)
            self.expected_strings.append(dv.name)
        self.expected_strings = [i.lower() for i in self.expected_strings]
        self.driver_skip_size = self.get_driver_skip_size(Config.skip_lambda)
        self.auton_skip_size = self.get_auton_skip_size(Config.skip_lambda)
        self.division_names = [i.name for i in self.divisions]

    def get_driver_skip_size(self, skip_lambda):
        shortest_driver = min([dv.driver_duration for dv in self.divisions if dv.driver_duration > 0])
        return skip_lambda(shortest_driver)

    def get_auton_skip_size(self, skip_lambda):
        shortest_auton = min([dv.auton_duration for dv in self.divisions if dv.auton_duration > 0])
        return skip_lambda(shortest_auton)

    def select_ocr_regions(self, time):
        for region in self.ocr_regions.keys():
            self.select_ocr_region(time, region)

    def select_ocr_region(self, time, field_type):
        frame_num = int(time * self.fps)
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

    def set_video_path(self, vid_path):
        self.video_path = vid_path
        self.video_obj = cv2.VideoCapture(self.video_path)
        self.set_fps_and_total_frames()

    def select_video_path(self):
        self.set_video_path(FileBrowser("Select video file", os.getcwd()).browse())

    def set_fps_and_total_frames(self):
        proc = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    "-show_entries", "stream=avg_frame_rate,nb_read_packets", self.video_path],
                   capture_output=True)
        output = proc.stdout.decode()
        fps_str, total_frames = output.split("\n", maxsplit=1)
        n, d = fps_str.split(r"/")
        self.fps = float(n) / float(d)
        self.frame_count = int(total_frames)
