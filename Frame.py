from OCR import OCR

class Frame:
    def __init__(self, video_pos, cv2_frame, ocr = False):
        self.video_pos = video_pos
        self.cv2_frame = cv2_frame
        self.timer_seconds = None
        self.timer_string = None
        self.match_num = None
        self.match_mode = None
        self.division_name = None
        self.full_ocr = False
        if ocr:
            results = OCR.analyze_frame(self.cv2_frame)
            (self.timer_seconds,
             self.timer_string,
             self.match_num,
             self.match_mode,
             self.division_name
             ) = results
            if None not in list(results):
                self.full_ocr = True

    def __str__(self):
        return "Frame Object\n" + \
                f"\tVideo Pos: {self.video_pos}\n" + \
                f"\tTimer Sec: {self.timer_seconds}\n" + \
                f"\tTimer Str: {self.timer_string}\n" + \
                f"\tMatch Num: {self.match_num}\n" + \
                f"\tMatch Mode: {self.match_mode}\n" + \
                f"\tDiv Name: {self.division_name}"

    def is_driver(self):
        return isinstance(self.match_mode, str) and "driver".lower() in self.match_mode.lower()

    def is_auton(self):
        return isinstance(self.match_mode, str) and "auton".lower() in self.match_mode.lower()

    def has_timer(self):
        return self.timer_seconds is not None

