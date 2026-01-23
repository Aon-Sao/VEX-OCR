import utils
from SearchGenerator import SearchGenerator
from VideoRegion import VideoRegion
from config import *
from VideoPosition import VideoPosition as vp


class Match:
    def __init__(self, initial_frame):
        self.match_num = initial_frame.match_num
        self.division_name = initial_frame.division_name
        self.division_type = "some_division_type"

        self.auton_region = None
        self.driver_region = None

        self.find_times(initial_frame)

    def __str__(self):
        return f"Match Object\n" + \
            f"\tMatch Num: {self.match_num}\n" + \
            f"\tDivision Name: {self.division_name}\n" + \
            f"\tDivision Type: {self.division_type}\n" + \
            f"\tAuton: {self.auton_region.replace("\n", "\n\t")}\n" + \
            f"\tDriver: {self.driver_region.replace("\n", "\n\t")}"

    def find_times(self, frame):
        self.find_driver_region(frame)
        auton_exists = CONFIG.division_types[self.division_type]["AUTON_DURATION"] > 0
        if auton_exists:
            self.find_auton_region()

    def find_driver_region(self, driver_frame):
        stop_pos = driver_frame.video_pos + vp(time=driver_frame.timer_seconds)
        # Assume the smallest driver time first. Go to where 2 seconds in should be.
        # See if the timer reflects our assumption. Try the next driver time.
        # Note that DIVISION_TYPES is sorted by ascending DRIVER_DURATION
        for div_name, div_values in CONFIG.division_types.items():
            backtrack_distance = div_values["DRIVER_DURATION"] - 2
            # or, check_pos = driver_frame.video_pos - (duration - timer)
            check_pos = stop_pos - vp(time=backtrack_distance)
            check_frame = utils.get_frame(check_pos)
            # lambda is just to evaluate exp after other checks and avoid comparing None to int
            timer_correct = lambda : backtrack_distance - 1 <= check_frame.timer_seconds <= backtrack_distance + 1
            if check_frame.is_driver() and check_frame.has_timer() and timer_correct():
                self.division_type = div_name
            else:
                break
        start_pos = stop_pos - vp(time=CONFIG.division_types[self.division_type]["DRIVER_DURATION"])
        self.driver_region = VideoRegion(start_pos, stop_pos)

    def find_auton_region(self):
        # TODO: Don't hardcode this
        max_search_time = 5 * 60
        driver_start_pos = self.driver_region.start() - vp(time=max_search_time)
        # Search backwards from driver start
        # If we want to assume the first frame we hit (in reverse) is the auton stop frame
        # then the skip_size must be 1 frame
        # shortest_division = list(CONFIG.division_types.items())[0][1]
        # half_shortest_auton = vp(time=shortest_division["DRIVER_AUTON"] / 2)
        gen = SearchGenerator(driver_start_pos).seconds_based_skip(vp(frame=1))
        frame, _ = utils.skip_search(gen, accept=lambda x: x.is_auton(), reject=lambda x: x.is_driver())
        auton_stop_pos = frame.video_pos
        auton_start_pos = auton_stop_pos - vp(CONFIG.division_types[self.division_type]["AUTON_DURATION"])
        self.auton_region = VideoRegion(auton_start_pos, auton_stop_pos)
