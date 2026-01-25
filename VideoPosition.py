import functools


# TODO: Prioritize frame over time
class VideoPosition:
    def __init__(self, config, frame: int = None, time: float | int = None):
        self.config = config
        self._frame, self._time = None, None
        if (frame is None) and (time is None):
            raise TypeError("Must specify either frame or time")
        elif time is not None:
            if isinstance(time, VideoPosition):
                time = time.time()  #...nice...
            elif not (isinstance(time, float) or isinstance(time, int)):
                raise TypeError(f"time must be a number, not {type(time)}")
            self._time = time
        elif frame is not None:  # frame is set
            if isinstance(frame, VideoPosition):
                self._frame = frame.frame()
            elif not isinstance(frame, int):
                raise TypeError(f"frame must be an int, not {type(frame)}")
            else:
                self._frame = frame

    def __str__(self):
        return str({"time": self.time(), "frame": self.frame()})

    def time(self):
        return self._time if self._time is not None else self._frame / self.config.fps

    def frame(self):
        return self._frame if self._frame is not None else round(self._time * self.config.fps)

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
        return VideoPosition(self.config, time=self.time() + other.time())

    @do_if_compatible
    def __sub__(self, other):
        return VideoPosition(self.config, time=self.time() - other.time())

    @do_if_compatible
    def __lt__(self, other):
        return self.time() < other.time()

    @do_if_compatible
    def __le__(self, other):
        return self.time() <= other.time()

    @do_if_compatible
    def __eq__(self, other):
        return self.time() == other.time()

    def __mul__(self, other):
        return VideoPosition(self.config, time=self.time() * other)

    def __truediv__(self, other):
        return VideoPosition(self.config, time=self.time() / other)