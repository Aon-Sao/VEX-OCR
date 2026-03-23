from ocr.VideoPosition import VideoPosition as VidPos
from ocr.VideoRegion import VideoRegion as VidReg
from ocr.FrameResolver import FrameResolver
from ocr.Config import CONFIG as config
from ocr.utils import get_frame


class PhaseResolver:
    def __init__(self, initial_frame: FrameResolver):
        self.initial_frame = initial_frame
        self.mode = initial_frame.match_mode
        self.match_num = initial_frame.match_name
        self.division_name = initial_frame.division_name
        self.program_type = initial_frame.program_type
        self.division = None
        self.duration = None
        self.region = self._find_region()
        self.verified = self._verify_region()

    def __str__(self):
        return self.region.__str__()

    def _frame_and_timer_to_stop(self):
        return self.initial_frame.video_pos + VidPos(time=self.initial_frame.timer_seconds)

    def _stop_and_div_type_to_start(self, stop):
        for dv in config.divisions:
            if dv.name.lower() == self.division_name.lower():
                self.division = dv
        self.duration = self.division.driver_duration if self.is_driver() else self.division.auton_duration
        return stop - VidPos(time=self.duration)

    def _find_region(self):
        stop = self._frame_and_timer_to_stop()
        start = self._stop_and_div_type_to_start(stop)
        return VidReg(start, stop)

    def is_driver(self):
        return self.mode == "driver"

    def is_auton(self):
        return self.mode == "auton"

    def _verify_region(self):
        # Do we need to verify anything besides just the timer?
        return self._verify_start() and self._verify_stop()

    def _verify_start(self):
        # Check that 5 seconds after the start of this phase,
        # The timer has 5 seconds missing from it
        check_pos = self.region.start() + VidPos(time=5)
        expected_timer_sec = self.duration - 5
        timer_correct = get_frame(check_pos).timer_seconds == expected_timer_sec
        return timer_correct

    def _verify_stop(self):
        # Check that 5 seconds before the end of this phase,
        # The timer has 5 seconds left on it
        check_pos = self.region.end() - VidPos(time=5)
        expected_timer_sec = 5
        timer_correct = get_frame(check_pos).timer_seconds == expected_timer_sec
        return timer_correct