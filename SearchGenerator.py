class SearchGenerator:
    class FramePos(int):
        pass
    class FrameDelta(int):
        pass
    class TimePos(float):
        pass
    class TimeDelta(float):
        pass

    def __init__(self, fps, start, stop=None):
        self.fps = fps
        self.start = start
        self.stop = stop

    def advance(self, pos, delta):
        if isinstance(pos, self.FramePos) and isinstance(delta, self.FrameDelta):
            return self.FramePos(pos + delta)
        elif isinstance(pos, self.TimePos) and isinstance(delta, self.TimeDelta):
            return self.TimePos(pos + delta)
        else:
            raise TypeError(f"Incompatible types {type(pos)} and {type(delta)}")

        # For when there is no information. Skipping by a "reasonable number of frames"
    def fps_based_skip(self):
        pass