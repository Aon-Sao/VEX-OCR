import functools
from decimal import Decimal
from Config import CONFIG as config


class VideoPosition:
    def __init__(self, frame: int = None, time: float | int = None):
        if ((frame is None) and (time is None)) or ((frame is not None) and (time is not None)):
            raise TypeError("Must specify either frame or time (exclusive)")
        elif isinstance(frame, VideoPosition):
            self._frame = frame.frame()
        elif isinstance(time, VideoPosition):
            self._frame = time.frame()
        elif isinstance(frame, int):
            self._frame = frame
        elif type(time) in [float, int, Decimal]:
            self._frame = round(time * config.fps)
        else:
            raise TypeError("time/frame must be one of: [float, int, Decimal, VideoPosition]")


    def __str__(self):
        return str({"time": self.time(), "frame": self.frame()})

    def time(self):
        return self._frame / config.fps

    def pretty_time(self):
        total_seconds = int(self.time())
        total_minutes = int(total_seconds // 60)
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        seconds = int(total_seconds % 60)
        return f"{hours}:{minutes}:{seconds}"

    def frame(self):
        return self._frame

    @staticmethod
    def do_if_compatible(func):
        @functools.wraps(func)
        def wrapper(self, other):
            if isinstance(other, VideoPosition):
                return func(self, other)
            else:
                raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")
        return wrapper

    @do_if_compatible
    def __add__(self, other):
        return VideoPosition(frame=self.frame() + other.frame())

    @do_if_compatible
    def __sub__(self, other):
        return VideoPosition(frame=self.frame() - other.frame())

    @do_if_compatible
    def __lt__(self, other):
        return self.frame() < other.frame()

    @do_if_compatible
    def __le__(self, other):
        return self.frame() <= other.frame()

    @do_if_compatible
    def __eq__(self, other):
        return self.frame() == other.frame()

    def __mul__(self, other):
        return VideoPosition(frame=self.frame() * other)

    def __truediv__(self, other):
        return VideoPosition(frame=self.frame() / other)