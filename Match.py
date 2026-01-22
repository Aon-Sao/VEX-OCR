from config import *

class Match:
    def __init__(self, m_finder):
        self.m_finder = m_finder
        self.match_num = "some_match_num"
        self.division_name = "some_division_name"
        self.division_type = "some_division_type"

        # We'll see which ones we use
        self.auton_start_frame = None
        self.auton_start_time = None
        self.auton_stop_frame = None
        self.auton_stop_time = None
        self.driver_start_frame = None
        self.driver_start_time = None
        self.driver_stop_frame = None
        self.driver_stop_time = None

    def __str__(self):
        return f"Match Object\n" + \
                f"Match Num: {self.match_num}\n" + \
                f"Division Name: {self.division_name}\n" + \
                f"Division Type: {self.division_type}\n" + \
                f"Auton times: {self.auton_start_time}s -- {self.auton_stop_time}s\n" + \
                f"Auton frames: {self.auton_start_frame}s -- {self.auton_stop_frame}s\n" + \
                f"Driver times: {self.driver_start_time}s -- {self.driver_stop_time}s\n" + \
                f"Driver frames: {self.driver_start_frame}s -- {self.driver_stop_frame}s\n"

    def find_times(self, frame):
        self.find_driver_stop(frame)
        self.find_driver_start()
        auton_exists = CONFIG.division_types[self.division_type]["AUTON_DURATION"] > 0
        if auton_exists:
            self.find_auton_stop()
            self.find_auton_start()

    def find_driver_stop(self, frame):
        self.driver_stop_time = self.m_finder.frame_num_to_time(frame.frame_num) + frame.timer_seconds
        self.driver_stop_frame = self.m_finder.time_to_frame_num(self.driver_stop_time)

    def find_driver_start(self):
        # Assume the smallest driver time first. Go to where 2 seconds in should be.
        # See if the timer reflects our assumption. Try the next driver time.
        # Note that DIVISION_TYPES is sorted by ascending DRIVER_DURATION
        for div_name, div_values in CONFIG.division_types.items():
            backtrack_distance = div_values["DRIVER_DURATION"] - 2
            check_time = self.driver_stop_time - backtrack_distance
            frame = self.m_finder.get_frame(self.m_finder.time_to_frame_num(check_time))
            timer_correct = backtrack_distance - 1 <= frame.timer_seconds <= backtrack_distance
            if self.m_finder.is_driver_frame(frame) and timer_correct:
                self.division_type = div_name
            else:
                break
        self.driver_start_time = self.driver_stop_time - CONFIG.division_types[self.division_type]["DRIVER_DURATION"]
        self.driver_start_frame = self.m_finder.time_to_frame_num(self.driver_start_time)

    def find_auton_stop(self):
        max_search_time = 5 * 60
        start = self.driver_start_time - max_search_time
        frame = self.m_finder.linear_search(
            start,
            self.driver_start_time,
            accept=self.m_finder.is_auton_frame,
            reject=self.m_finder.is_driver_frame,
            forwards=False,
            ocr=False
        )
        self.auton_stop_frame = frame.frame_num
        self.auton_stop_time = self.m_finder.frame_num_to_time(self.auton_stop_frame)

    def find_auton_start(self):
        self.auton_start_time = self.auton_stop_time - CONFIG.division_types[self.division_type]["AUTON_DURATION"]

    def has_driver(self):
        return any([bool(i) for i in [
            self.driver_start_frame,
            self.driver_start_time,
        ]]) and any([bool(i) for i in [
            self.driver_stop_frame,
            self.driver_stop_time,
        ]])

    def has_auton(self):
        return any([bool(i) for i in [
            self.auton_start_frame,
            self.auton_start_time,
        ]]) and any([bool(i) for i in [
            self.auton_stop_frame,
            self.auton_stop_time,
        ]])