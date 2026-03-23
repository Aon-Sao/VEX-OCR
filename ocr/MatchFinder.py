import utils
from Config import CONFIG as config
from DatabaseInteractor import DatabaseInteractor
from MatchResolver import MatchResolver
from SearchGenerator import SearchGenerator
from VideoPosition import VideoPosition as VidPos

class MatchFinder:
    # Singleton
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.furthest_pos = VidPos(time=config.scan_start_offset)

    def find_all_matches(self):
        video_end = VidPos(frame=config.frame_count)
        shortest_driver = min([dv.driver_duration for dv in config.divisions if dv.driver_duration > 0])

        start = self.furthest_pos
        skip_size = VidPos(frame=config.driver_skip_size)

        matches_may_remain = True
        while matches_may_remain:
            print(f"Progress: {(self.furthest_pos.frame() / video_end.frame()) * 100:.0f}%")
            gen = SearchGenerator(start, video_end).seconds_based_skip(skip_size)
            if (match := self.find_next_match(gen)) is not None:
                if match.complete():
                    print(f"DEBUG: complete match\n{match}")
                    start = self.process_found_match(match)
                elif match.driver is not None:
                    print(f"DEBUG: partial match\n{match}")
                    start = match.driver.region.end()
                elif match.auton is not None:
                    print(f"DEBUG: partial match\n{match}")
                    start = match.auton.region.end()
                else:
                    print(f"DEBUG: partial match\n{match}")
                    start = self.furthest_pos
            matches_may_remain = self.furthest_pos < (video_end - VidPos(time=shortest_driver))

    def find_next_match(self, search_generator: SearchGenerator):
        print(f"DEBUG: searching for driver phase")
        frame, furthest_pos = utils.skip_search(search_generator)
        self.furthest_pos = furthest_pos
        return MatchResolver(frame) if frame else None

    @staticmethod
    def process_found_match(match: MatchResolver):
        match_info = match.get_data_obj()
        dbi = DatabaseInteractor(config.pg_conn_str)
        dbi.update_found_match(match_info)
        return match.driver.region.end()