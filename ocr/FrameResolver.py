import utils
from VideoPosition import VideoPosition as VidPos
from OCR import Ocr

class FrameResolver:
    def __init__(self, video_pos: VidPos, cv2_frame, ocr = False):
        self.video_pos = video_pos
        self.cv2_frame = cv2_frame
        self.timer_seconds = None
        self.timer_string = None
        self.match_name = None
        self.match_mode = None
        self.division_name = None
        self.program_type = None
        self._full_ocr = False

        if ocr:
            results = Ocr.analyze_frame(self.cv2_frame)
            (self.timer_seconds,
             self.timer_string,
             self.match_name,
             self.match_mode,
             self.division_name,
             self.program_type
             ) = results
            if None not in list(results):
                self._full_ocr = True

    def __str__(self):
        return "Frame Object\n" + \
                f"\tVideo Pos: {self.video_pos}\n" + \
                f"\tTimer Sec: {self.timer_seconds}\n" + \
                f"\tTimer Str: {self.timer_string}\n" + \
                f"\tMatch Num: {self.match_name}\n" + \
                f"\tMatch Mode: {self.match_mode}\n" + \
                f"\tDiv Name: {self.division_name}"

    def is_driver(self):
        return self.match_mode == "driver"

    def is_auton(self):
        return self.match_mode == "auton"

    def has_timer(self):
        return self.timer_seconds is not None

    def full_ocr(self):
        return self._full_ocr

    def show(self):
        utils.display_img(self.cv2_frame)