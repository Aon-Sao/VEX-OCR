from VideoRegion import VideoRegion
from VideoPosition import VideoPosition as vp

class PhaseResolver:
    def __init__(self, config, initial_frame):
        self.config = config
        self.initial_frame = initial_frame
        self.mode = initial_frame.match_mode
        self.match_num = initial_frame.match_num
        self.division_name = initial_frame.division_name
        self.division_type = initial_frame.division_type
        self.region = self._find_region()

    def __str__(self):
        return self.region.__str__()

    def _frame_and_timer_to_stop(self):
        return self.initial_frame.video_pos + vp(self.config, time=self.initial_frame.timer_seconds)

    def _stop_and_div_type_to_start(self, stop):
        dv = [dv for dv in self.config.divisions if dv.program_code == self.division_type][0]
        duration = dv.driver_duration if self.mode == "driver" else dv.auton_duration
        return stop - vp(self.config, time=duration)

    def _find_region(self):
        stop_pos = self._frame_and_timer_to_stop()
        start_pos = self._stop_and_div_type_to_start(stop_pos)
        region = VideoRegion(start_pos, stop_pos)
        return region

    def is_driver(self):
        return self.mode == "driver"

    def is_auton(self):
        return self.mode == "auton"