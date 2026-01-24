import os
from subprocess import run
import cv2
from FileBrowser import FileBrowser
from Event import _V5RC, _VURC, _VIQRC

class Config:
    # Singleton
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    class events:  # So we can write CONFIG.events.V5RC.driver_duration, etc.
        V5RC = _V5RC(
            event_sku="some_event_sku",
            division_names=[
                "some_division_name_1",
                "some_division_name_2",
            ],
        )
        VURC = _VURC(
            event_sku="some_event_sku",
            division_names=[
                "Technology",
            ],
        )
        VIQRC = _VIQRC(
            event_sku="some_event_sku",
            division_names=[
                "some_division_name_5",
                "some_division_name_6",
            ],
        )

        def __iter__(self):
            return [self.V5RC, self.VURC, self.VIQRC].__iter__()

        def __len__(self):
            return [self.V5RC, self.VURC, self.VIQRC].__len__()

        def __getitem__(self, item):
            return {"V5RC": self.V5RC, "VURC": self.VURC, "VIQRC": self.VIQRC}.__getitem__(item)

    events = events()

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
    stream_id = -1
    division_id = -1

    def __init__(self):
        # Only modify values above
        self.video_path = None
        self.frame_count = None
        self.fps = None
        self.video_obj = None
        for ev in self.events:
            self.expected_strings.append(ev.prog_type)
            self.expected_strings.extend(ev.division_names)
        self.expected_strings = [i.lower() for i in self.expected_strings]
        self.driver_skip_size = self.get_driver_skip_size(Config.skip_lambda)
        self.auton_skip_size = self.get_auton_skip_size(Config.skip_lambda)
        # I will confess the below comprehension is incomprehensible
        # I leave it in, for now, for the sake of practice
        # It makes a list of all the division names in all the events
        self.division_names = [name for ev in self.events for name in ev.division_names]

    def get_driver_skip_size(self, skip_lambda):
        shortest_driver = min([ev.driver_duration for ev in self.events if ev.driver_duration > 0])
        return skip_lambda(shortest_driver)

    def get_auton_skip_size(self, skip_lambda):
        shortest_auton = min([ev.auton_duration for ev in self.events if ev.auton_duration > 0])
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


CONFIG = Config()