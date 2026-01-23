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
        # Wrap with list() to allow subscription
        shortest_division = list(CONFIG.division_types.items())[0][1]
        shortest_driver = vp(time=shortest_division["DRIVER_DURATION"])
        shortest_possible_match = vp(time=shortest_driver.time() + shortest_division["AUTON_DURATION"])

        start = vp(frame=0)
        end = video_end
        skip_size = shortest_driver / 2

        matches = []
        while self.furthest_pos < (video_end - shortest_possible_match):
            gen = SearchGenerator(start, end).seconds_based_skip(skip_size)
            if (match := self.find_next_match(gen)) is not None:
                matches.append(match)
                previous_match = matches[-1]
                start = previous_match.driver_region.end()
        return matches

    def find_next_match(self, frame_generator):
        frame, self.furthest_pos = utils.skip_search(frame_generator)
        return Match(frame) if frame else None
