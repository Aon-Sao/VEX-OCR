import os
from subprocess import run

import cv2
from collections import OrderedDict

from FileBrowser import FileBrowser

class Config:
    # Singleton
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    #! Unhandled edge case: the sorting of the driver durations isn't also the sorting of the auton durations
    division_types = OrderedDict(sorted({
        "V5RC": {
            "DRIVER_DURATION": 105,
            "AUTON_DURATION": 15
        },
        "VURC": {
            "DRIVER_DURATION": 75,
            "AUTON_DURATION": 45
        },
        "VIQRC": {
            "DRIVER_DURATION": 60,
            "AUTON_DURATION": 0
        }}.items(), key=lambda d: d[1]["DRIVER_DURATION"]))
    ocr_regions = {
        "DEFAULT": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
            "MATCH_MODE": [0, 0, 0, 0],
        },
        "V5RC": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
        },
        "VURC": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
        },
        "VIQRC": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
        },
    }
    division_types_present = [
        "VIQRC",
        "V5RC",
        "VURC"
    ]
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
    stream_id = -1
    division_id = -1
    division_names = ["Design Division"]
    event_skus = []

    def __init__(self):
        # Do not set these values by hand
        self.video_path = None
        self.frame_count = None
        self.fps = None
        self.video_obj = None
        self.expected_strings.extend(self.division_names)
        self.expected_strings.extend(self.division_types_present)
        self.expected_strings = [i.lower() for i in self.expected_strings]

    def select_ocr_regions(self, time, division_type="DEFAULT"):
        for region in self.ocr_regions[division_type].keys():
            self.select_ocr_region(time, division_type, region)

    def select_ocr_region(self, time, division_type, field_type):
        assert division_type in self.ocr_regions.keys()
        vid = cv2.VideoCapture(self.video_path)
        frame_num = int(time * vid.get(cv2.CAP_PROP_FPS))
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = vid.read()
        title = f"Select {division_type} {field_type}"
        sel = self.select_region(frame, title)
        self.ocr_regions[division_type][field_type] = list(sel)

    def select_region(self, img, title="Select region"):
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


CONFIG = Config()