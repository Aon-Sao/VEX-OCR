from OCR import OCR

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

    def __str__(self):
        return "Frame Object\n" + \
                f"Frame Num: {self.frame_num}\n" + \
                f"Timer Sec: {self.timer_seconds}\n" + \
                f"Timer Str: {self.timer_string}\n" + \
                f"Match Num: {self.match_num}\n" + \
                f"Match Mode: {self.match_mode}\n" + \
                f"Div Name: {self.division_name}\n"

    def ocr(self):
        self.timer_seconds, self.match_num, self.match_mode, self.division_name = OCR.analyze_frame(self.cv2_frame)
        self.timer_string = f"{self.timer_seconds // 60}:{self.timer_seconds % 60}"
