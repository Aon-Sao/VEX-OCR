import cv2
from Frame import Frame
from Match import Match


class MatchFinder:
    def __init__(self, video):
        self.video = cv2.VideoCapture(video)
        self.total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.duration_seconds = self.total_frames / self.fps

    def is_driver_frame(self, frame):
        # Match mode says driver && timer is non-zero
        if not isinstance(frame.match_mode, str):
            return False
        return "driver".lower() in frame.match_mode.lower() \
            and frame.timer_seconds > 0

    def is_auton_frame(self, frame):
        # Match mode says auton && timer is non-zero
        if not isinstance(frame.match_mode, str):
            return False
        return "auton".lower() in frame.match_mode.lower() \
            and frame.timer_seconds > 0

    def get_frame(self, frame_num, ocr = True):
        print(f"DEBUG: getting frame {frame_num}, OCR: {ocr}")
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.video.read()
        return Frame(frame_num, frame, ocr=ocr)

    def find_first_match(self):
        frame = self.linear_search(0, self.total_frames - 1, accept=self.is_driver_frame)
        return self.dframe_to_match(frame)

    def find_next_match(self, previous_match):
        pass

    def dframe_to_match(self, frame):
        match = Match(self) # hmmm
        match.match_num = frame.match_num
        match.division_name = frame.division_name
        match.find_times(frame)
        return match

    def time_to_frame_num(self, s):
        return int(s * self.fps)

    def frame_num_to_time(self, f):
        return f / self.fps

    def linear_search(self, start, end, accept = None, reject = None, forwards = True, ocr = True):
        print(f"DEBUG: searching from {start} to {end}" + ("" if forwards else "in reverse"))
        # By default, we are looking for driver frames
        if accept is None:
            accept = self.is_driver_frame
        # If there is no reject condition, don't halt early
        if reject is None:
            reject = lambda x: False
        frame_nums = range(int(start + 1), int(end))
        if not forwards:
            frame_nums = reversed(frame_nums)

        for n in frame_nums:
            frame = self.get_frame(n, ocr=ocr)
            if accept(frame):
                return frame
            elif reject(frame):
                break

        return None
