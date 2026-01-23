from VideoPosition import VideoPosition as vp

class SearchGenerator:

    def __init__(self, start, stop=None):
        self.start = vp(time=start)
        self.stop = vp(time=stop) if stop is not None else None
        self.pos = self.start

    def communicator(self, func):
        msg = ("CONTINUE",)
        while msg[0] == "CONTINUE":
            msg = yield self.pos
            func(*msg)

    # Skipping by a "reasonable number of frames"
    # Pass negative values to go in reverse
    def seconds_based_skip(self, skip_size):
        def skipper(msg, frame):
            self.pos += skip_size
        return self.communicator(skipper)

