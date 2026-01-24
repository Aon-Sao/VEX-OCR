import utils
from Phase import Phase
from SearchGenerator import SearchGenerator
from config import *
from VideoPosition import VideoPosition as vp


class Match:
    def __init__(self, initial_frame):
        self.initial_frame = initial_frame
        self.match_num = initial_frame.match_num
        self.division_name = initial_frame.division_name
        self.division_type = initial_frame.division_type
        self.event = CONFIG.events[self.division_type]
        self.auton = None
        self.driver = None

        self.find_phases()

    def complete(self):
        return None not in [
            self.match_num,
            self.division_name,
            self.division_type,
            self.auton,
            self.driver,
            self.event,
        ]

    def __str__(self):
        return f"Match Object\n" + \
                ("INCOMPLETE!\n" if not self.complete() else "") + \
                f"\tMatch Num: {self.match_num}\n" + \
                f"\tDivision Name: {self.division_name}\n" + \
                f"\tDivision Type: {self.division_type}\n" + \
                f"\tAuton: {str(self.auton).replace("\n", "\n\t       ")}\n" + \
                f"\tDriver: {str(self.driver).replace("\n", "\n\t        ")}"

    def find_phases(self):
        # TODO: handle no auton, e.g. VIQRC
        initial_phase = Phase(self.initial_frame)
        if initial_phase.is_driver():
            self.driver = initial_phase
            self.auton = self._find_adjacent_phase(search_ahead=False)
        elif initial_phase.is_auton():
            self.auton = initial_phase
            self.driver = self._find_adjacent_phase(search_ahead=True)

    # Could probably combine with above method later
    def _find_adjacent_phase(self, search_ahead=False):
        if search_ahead:  # For driver
            start = self.auton.region.end()
            end = start + vp(time=CONFIG.max_phase_distance)
            skip = CONFIG.driver_skip_size
            accept = lambda x: x.is_driver() and x.full_ocr() and x.match_num == self.match_num
            reject = lambda x: x.is_auton()
        else:  # Search behind for auton
            end = self.driver.region.start()
            start = end - vp(time=CONFIG.max_phase_distance)
            skip = CONFIG.auton_skip_size * -1  # Need to actually search backwards
            accept = lambda x: x.is_auton() and x.full_ocr() and x.match_num == self.match_num
            reject = lambda x: x.is_driver()
        gen = SearchGenerator(start, end).seconds_based_skip(skip)
        frame, _ = utils.skip_search(gen, accept, reject)
        return Phase(frame) if frame is not None else None
