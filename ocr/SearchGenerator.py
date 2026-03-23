from copy import deepcopy
from ocr.VideoPosition import VideoPosition as VidPos
from ocr.Config import CONFIG as config

import logging

log = logging.getLogger(__name__)


class SearchGenerator:

    def __init__(self, start: VidPos, stop: VidPos | None = None):
        self.start = start
        self.stop = stop
        self.pos = self.start

    def communicator(self, func):
        msg = ("CONTINUE",)
        while msg[0] == "CONTINUE":
            func(*msg)
            if not (VidPos(frame=0) <= self.pos <= VidPos(frame=config.frame_count)):
                break
            msg = yield self.pos

    # Skipping by a "reasonable number of frames"
    # Pass negative values to go in reverse
    def seconds_based_skip(self, skip_size: VidPos):
        if skip_size > VidPos(frame=0):
            log.info(
                f"Searching {self.start.frame()} --> {self.stop.frame()} {self.start.pretty_time()} --> {self.stop.pretty_time()}")
        else:
            log.info(
                f"Searching {self.stop.frame()} <-- {self.start.frame()} {self.stop.pretty_time()} <-- {self.start.pretty_time()}")

        def skipper(msg, frame):
            self.pos += skip_size

        return self.communicator(skipper)

    # Jump to positions in a list
    def list_based_skip(self, lst):
        _lst = list(deepcopy(lst))

        def jumper(msg, frame):
            self.pos = _lst.pop(0)

        return self.communicator(jumper)
