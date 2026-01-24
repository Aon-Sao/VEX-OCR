import utils
from config import CONFIG
from Match import Match
from SearchGenerator import SearchGenerator
from VideoPosition import VideoPosition as vp


class MatchFinder:
    # Singleton
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    furthest_pos = vp(time=0)

    # TODO: picking up from end of match should be a last resort
    def find_all_matches(self):
        video_end = vp(frame=CONFIG.frame_count)
        shortest_event = min(CONFIG.events, key=lambda ev: ev.auton_duration + ev.driver_duration)
        shortest_possible_match = vp(time=shortest_event.auton_duration + shortest_event.driver_duration)

        start = vp(frame=0)
        end = video_end
        # We don't mind whether we miss auton as long as we hit driver
        skip_size = vp(time=max(CONFIG.driver_skip_size, CONFIG.auton_skip_size))

        while self.furthest_pos < (video_end - shortest_possible_match):
            print(f"Progress: {(self.furthest_pos.frame() / video_end.frame()) * 100}%")
            gen = SearchGenerator(start, end).seconds_based_skip(skip_size)
            if (match := self.find_next_match(gen)) is not None:
                if match.complete():
                    start = match.driver.region.end()
                elif match.driver is not None:
                    start = match.driver.region.end()
                elif match.auton is not None:
                    start = match.auton.region.end()
                utils.send_match(match)

    def find_next_match(self, frame_generator):
        frame, self.furthest_pos = utils.skip_search(frame_generator)
        return Match(frame) if frame else None
