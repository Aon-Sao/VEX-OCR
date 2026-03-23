import re

import utils
from Config import CONFIG as config
from PhaseResolver import PhaseResolver
from SearchGenerator import SearchGenerator
from VideoRegion import VideoRegion as VidReg
from VideoPosition import VideoPosition as VidPos
import DataObjects
from FrameResolver import FrameResolver


class MatchResolver:
    def __init__(self, initial_frame: FrameResolver):
        self.ignore_auton = False
        self.initial_frame = initial_frame
        self.match_name = initial_frame.match_name
        self.division_name = initial_frame.division_name
        self.program_type = initial_frame.program_type
        self.auton, self.driver = self.find_phases()
        if self.complete():
            start = self.driver.region.start() if self.ignore_auton else self.auton.region.start()
            self.region = VidReg(start, self.driver.region.end())

    def complete(self):
        return None not in [
            self.match_name,
            self.division_name,
            self.program_type,
            self.driver
        ] and (self.ignore_auton or (self.auton is not None))

    def __str__(self):
        return f"Match Object\n" + \
            ("INCOMPLETE!\n" if not self.complete() else "") + \
            f"\tMatch Num: {self.match_name}\n" + \
            f"\tDivision Name: {self.division_name}\n" + \
            f"\tProgram Type: {self.program_type}\n" + \
            f"\tAuton: {str(self.auton).replace("\n", "\n\t       ")}\n" + \
            f"\tDriver: {str(self.driver).replace("\n", "\n\t        ")}"


    def get_data_obj(self):
        event_sku, div_id = self.event_sku_and_division_id_lookup()
        rnd, match_num, instance = self.match_name_parser()
        return DataObjects.Match(self.region.start().time(), self.region.end().time(), event_sku, div_id, rnd, instance, match_num)

    def event_sku_and_division_id_lookup(self):
        for div in config.divisions:
            if self.division_name == div.name:
                return div.event_sku, div.id
        return None

    def match_name_parser(self):
        exp = re.compile(r"(practice|qualification|qual|teamwork|final|qf|sf|r16|r32|r64|r128)\s?#?\s?(\d+)\s?-?\s?(\d+)?")
        if mat := re.match(exp, self.match_name.lower()):
            name_str = mat.group(1)
            num_str = mat.group(2)
            instance_str = mat.group(3) if mat.group(3) else "1"
            match_name_enum_dct = {
                "practice": 1,
                "qualifier": 2,
                "qual": 2,
                "teamwork": 2,
                "qf": 3,
                "sf": 4,
                "final": 5,
                "r16": 6,
                "match": 15
            }
            rnd = match_name_enum_dct[name_str]
            return int(rnd), int(num_str), int(instance_str)
        else:
            return None

    def find_phases(self):
        print(f"DEBUG: resolving driver phase")
        driver_phase = PhaseResolver(self.initial_frame)
        if driver_phase.division.auton_duration > 0:
            start = driver_phase.region.start()
            end = start - VidPos(time=config.max_phase_distance)
            skip = VidPos(frame=config.auton_skip_size * -1)
            accept = lambda x: x.is_auton() and x.full_ocr() and x.match_name  == self.match_name
            # skipping a reject lambda
            gen = SearchGenerator(start, end).seconds_based_skip(skip)
            print(f"DEBUG: searching for auton phase")
            frame, _ = utils.skip_search(gen, accept)
            print(f"DEBUG: resolving auton phase")
            auton_phase = PhaseResolver(frame) if frame is not None else None
        else:
            auton_phase = None
            self.ignore_auton = True
        return auton_phase, driver_phase
