import re

import ocr.utils as utils
import ocr.DataObjects as DataObjects
from ocr.Config import CONFIG as config
from ocr.PhaseResolver import PhaseResolver
from ocr.SearchGenerator import SearchGenerator
from ocr.VideoRegion import VideoRegion as VidReg
from ocr.VideoPosition import VideoPosition as VidPos
from ocr.FrameResolver import FrameResolver

import logging

log = logging.getLogger(__name__)


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
        event_sku = self.event_sku_lookup()
        return DataObjects.Match(
            video_id=config.video_id,
            worker_host=config.worker_host,
            event_sku=event_sku,
            division_name=self.division_name,
            match_name=self.match_name,
            auton_start_sec=self.auton.region.start().time() if self.auton else None,
            auton_start_frame=self.auton.region.start().frame() if self.auton else None,
            auton_stop_sec=self.auton.region.end().time() if self.auton else None,
            auton_stop_frame=self.auton.region.end().frame() if self.auton else None,
            driver_start_sec=self.driver.region.start().time() if self.driver else None,
            driver_start_frame=self.driver.region.start().frame() if self.driver else None,
            driver_stop_sec=self.driver.region.end().time() if self.driver else None,
            driver_stop_frame=self.driver.region.end().frame() if self.driver else None,
            found_complete_match=self.complete(),
            notes=None,
        )

    def event_sku_lookup(self):
        for div in config.divisions:
            if self.division_name == div.division_name:
                return div.event_sku
        return None

    def find_phases(self):
        log.info(f"Resolving driver phase")
        driver_phase = PhaseResolver(self.initial_frame)
        if driver_phase.division.auton_duration > 0:
            start = driver_phase.region.start()
            end = start - VidPos(time=config.max_phase_distance)
            skip = VidPos(frame=config.auton_skip_size * -1)
            start += skip  # do not OCR the first driver frame again
            accept = lambda x: x.is_auton() and x.full_ocr() and x.match_name == self.match_name
            # skipping a reject lambda
            log.info(f"Searching for auton phase")
            frame, _ = utils.skip_search(start, end, skip, accept)
            log.info(f"Resolving auton phase")
            auton_phase = PhaseResolver(frame) if frame is not None else None
        else:
            auton_phase = None
            self.ignore_auton = True
        return auton_phase, driver_phase
