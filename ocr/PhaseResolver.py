from ocr.Config import CONFIG as config
from ocr.DataObjects import Division
from ocr.FrameResolver import FrameResolver
from ocr.VideoPosition import VideoPosition as VidPos
from ocr.VideoRegion import VideoRegion as VidReg
from ocr.utils import get_frame


class PhaseResolver:
    def __init__(self, initial_frame: FrameResolver) -> None:
        self.initial_frame: FrameResolver = initial_frame
        self.match_mode: str = initial_frame.match_mode
        self.match_name: str = initial_frame.match_name
        self.division_name: str = initial_frame.division_name
        self.division: Division | None = None
        self.duration: VidPos | None = None
        self.region: VidReg = self.compute_edges()
        self.quality_rating: tuple[int, int] = self.quality_check(config.num_phase_quality_checks)

    def __str__(self) -> str:
        return self.region.__str__() + f"\nQuality Rating: {self.quality_rating}"

    def compute_left_edge(self) -> VidPos:
        return self.initial_frame.video_pos + VidPos(time=self.initial_frame.timer_seconds)

    def compute_right_edge(self, stop: VidPos) -> VidPos:
        for dv in config.divisions:
            if dv.division_name.lower() == self.division_name.lower():
                self.division = dv
        self.duration = self.division.driver_duration if self.is_driver() else self.division.auton_duration
        self.duration = VidPos(time=self.duration)
        return stop - self.duration

    def compute_edges(self) -> VidReg:
        stop = self.compute_left_edge()
        start = self.compute_right_edge(stop)
        return VidReg(start, stop)

    def is_driver(self) -> bool:
        return self.match_mode == "driver"

    def is_auton(self) -> bool:
        return self.match_mode == "auton"

    def validate_frame(self, frame: FrameResolver) -> bool:
        def close_enough(observed: int, expected: int):
            # Now we don't have to worry about floats or off-by-one
            return expected - 1 <= observed <= expected + 1

        seconds_delta = (self.initial_frame.video_pos - frame.video_pos).time()
        expected_timer_seconds = self.initial_frame.timer_seconds + seconds_delta

        if not frame.full_ocr():
            return False
        else:
            name_correct = frame.match_name == self.match_name
            mode_correct = frame.match_mode == self.match_mode
            timer_correct = close_enough(frame.timer_seconds, expected_timer_seconds)
            return name_correct and mode_correct and timer_correct

    def quality_check(self, num_checks: int) -> tuple[int, int]:
        start = self.region.start().frame()
        end = self.region.end().frame()
        skip = (self.duration // num_checks).frame()
        check_positions = [VidPos(i) for i in range(start, end, skip)]
        passes = 0
        for pos in check_positions:
            frame = get_frame(pos, ocr=True)
            if self.validate_frame(frame):
                passes += 1
        return passes, num_checks