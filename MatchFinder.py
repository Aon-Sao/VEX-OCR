from utils import *
import cv2
from Match import Match


class MatchFinder:
    def __init__(self, video):
        self.video = cv2.VideoCapture(video)
        self.total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.duration_seconds = self.total_frames / self.fps

    def find_first_match(self):
        # TODO: Put the generator in
        frame = self.skip_search()
        return Match(self, frame)  # hmmm

    def find_next_match(self, previous_match):
        pass

    def skip_search(self, frame_generator, accept=None, reject=None, ocr=True):
        # By default, we are looking for driver frames
        if accept is None:
            accept = is_driver_frame
        # If there is no reject condition, don't halt early
        if reject is None:
            reject = lambda x: False
        for n in frame_generator:
            frame = get_frame(self.video, n, ocr=ocr)
            if accept(frame):
                return frame
            elif reject(frame):
                break
        return None