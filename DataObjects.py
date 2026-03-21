from typing import Optional

import msgspec

class Division(msgspec.Struct):
    program_code: str
    name: str
    event_sku: str
    id: int
    driver_duration: Optional[int] = None
    auton_duration: Optional[int] = None

    def __post_init__(self):
        match self.program_code:
            case "V5RC":
                self.driver_duration = 105
                self.auton_duration = 15
            case "VURC":
                self.driver_duration = 75
                self.auton_duration = 45
            case "VIQRC":
                self.driver_duration = 60
                self.auton_duration = 0
            case _:
                raise Exception("Unknown program_code in InputData")

    def has_auton(self):
        return self.auton_duration > 0

class OCRRegions(msgspec.Struct):
    MATCH_NUM: list[int]
    DIVISION_NAME: list[int]
    MATCH_TIMER: list[int]
    MATCH_MODE: list[int]

    def __post_init__(self):
        for attr in ["MATCH_NUM", "DIVISION_NAME", "MATCH_TIMER", "MATCH_MODE"]:
            if hasattr(self, attr) and ((val := getattr(self, attr)) is not None):
                assert len(val) == 4


class InputData(msgspec.Struct):
    scan_start_offset: int  # Seconds
    pg_conn_str: str
    ssd_vid_path: str
    divisions: list[Division]
    ocr_regions: OCRRegions
    search_algorithm: str = "classic"

class Match(msgspec.Struct):
    start: int
    end: int
    event_sku: str
    division_id: int
    round: int
    instance: int
    match_num: int
