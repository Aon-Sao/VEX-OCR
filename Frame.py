class Frame:
    def __init__(self, frame_num, cv2_frame, ocr = False):
        self.frame_num = frame_num
        self.cv2_frame = cv2_frame
        self.timer_seconds = None
        self.timer_string = None
        self.match_num = None
        self.match_mode = None
        self.division_name = None
        if ocr:
            self.ocr()

    def ocr(self):
        self.timer_string = "some_timer_string"
        self.timer_seconds = "some_timer_seconds"
        self.match_num = "some_match_num"
        self.match_mode = "some_match_mode"
        self.division_name = "some_division_name"
