from copy import deepcopy
from VideoPosition import VideoPosition as vp


class SearchGenerator:

    def __init__(self, config, start, stop=None):
        self.config = config
        self.start = vp(self.config, time=start)
        self.stop = vp(self.config, time=stop) if stop is not None else None
        self.pos = self.start

    def communicator(self, func):
        msg = ("CONTINUE",)
        while msg[0] == "CONTINUE":
            if not (vp(self.config, frame=0) <= self.pos <= vp(self.config, frame=self.config.frame_count)):
                break
            msg = yield self.pos
            func(*msg)

    # Skipping by a "reasonable number of frames"
    # Pass negative values to go in reverse
    def seconds_based_skip(self, skip_size):
        skip_size = vp(self.config, time=skip_size)
        def skipper(msg, frame):
            self.pos += skip_size
        return self.communicator(skipper)

    # Jump to positions in a list
    def list_based_skip(self, lst):
        _lst = list(deepcopy(lst))
        def jumper(msg, frame):
            self.pos = _lst.pop(0)
        return self.communicator(jumper)

