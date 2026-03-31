import functools
from decimal import Decimal
from numbers import Number

from ocr.Config import CONFIG as config


@functools.total_ordering
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

    def pretty_time(self):
        total_seconds = int(self.time())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def time(self):
        return self._frame / config.fps

    def frame(self):
        return self._frame

    def __str__(self):
        return str({"time": self.time(), "frame": self.frame()})

    def __hash__(self):
        return self.frame().__hash__()

    def __abs__(self):
        return VideoPosition(frame=self.frame().__abs__())

    def __lt__(self, other) -> VideoPosition:
        if isinstance(other, Number):
            return self.frame() < other
        elif isinstance(other, VideoPosition):
            return self.frame() < other.frame()
        else:
            raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")

    def __eq__(self, other) -> VideoPosition:
        if isinstance(other, Number):
            return self.frame() == other
        elif isinstance(other, VideoPosition):
            return self.frame() == other.frame()
        else:
            raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")

    def __add__(self, other) -> VideoPosition:
        if isinstance(other, Number):
            return VideoPosition(frame=self.frame() + other)
        elif isinstance(other, VideoPosition):
            return VideoPosition(frame=self.frame() + other.frame())
        else:
            raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")

    def __sub__(self, other) -> VideoPosition:
        if isinstance(other, Number):
            return VideoPosition(frame=self.frame() - other)
        elif isinstance(other, VideoPosition):
            return VideoPosition(frame=self.frame() - other.frame())
        else:
            raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")

    def __mul__(self, other) -> VideoPosition:
        if isinstance(other, Number):
            return VideoPosition(frame=self.frame() * other)
        elif isinstance(other, VideoPosition):
            return VideoPosition(frame=self.frame() * other.frame())
        else:
            raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")

    def __truediv__(self, other) -> VideoPosition:
        if isinstance(other, Number):
            return VideoPosition(frame=self.frame() / other)
        elif isinstance(other, VideoPosition):
            return VideoPosition(frame=self.frame() / other.frame())
        else:
            raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")

    def __floordiv__(self, other) -> VideoPosition:
        if isinstance(other, Number):
            return VideoPosition(frame=self.frame() // other)
        elif isinstance(other, VideoPosition):
            return VideoPosition(frame=self.frame() // other.frame())
        else:
            raise TypeError(f"Incompatible types: {type(self)} and {type(other)}")
