import utils
from MatchResolver import MatchResolver
from SearchGenerator import SearchGenerator
from VideoPosition import VideoPosition as vp


class MatchFinder:
    # Singleton
    instance = None
    def __new__(cls, config):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.config = config
        self.furthest_pos = vp(self.config, time=0)


    # TODO: picking up from end of match should be a last resort
    def find_all_matches(self):
        video_end = vp(self.config, frame=self.config.frame_count)
        shortest_division = min(self.config.divisions, key=lambda ev: ev.auton_duration + ev.driver_duration)
        shortest_possible_match = vp(self.config, time=shortest_division.auton_duration + shortest_division.driver_duration)

        start = vp(self.config, frame=0)
        end = video_end
        # We don't mind whether we miss auton as long as we hit driver
        skip_size = vp(self.config, time=max(self.config.driver_skip_size, self.config.auton_skip_size))

        while self.furthest_pos < (video_end - shortest_possible_match):
            print(f"Progress: {(self.furthest_pos.frame() / video_end.frame()) * 100}%")
            gen = SearchGenerator(self.config, start, end).seconds_based_skip(skip_size)
            if (match := self.find_next_match(gen)) is not None:
                if match.complete():
                    start = match.driver.region.end()
                elif match.driver is not None:
                    start = match.driver.region.end()
                elif match.auton is not None:
                    start = match.auton.region.end()
                utils.send_match(match)

    def find_next_match(self, frame_generator):
        frame, self.furthest_pos = utils.skip_search(self.config, frame_generator)
        return MatchResolver(self.config, frame) if frame else None
