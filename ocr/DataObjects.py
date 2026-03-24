from typing import Optional

import msgspec

class Division(msgspec.Struct):
    event_sku: str
    program_code: str
    division_name: str
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
    pg_conn_str: str
    ssd_vid_path: str
    scan_start_offset: int  # Seconds
    divisions: list[Division]
    video_id: int
    worker_host: str
    ocr_regions: OCRRegions

class Match(msgspec.Struct):
    video_id: int
    worker_host: int
    event_sku: str
    division_name: str
    match_name: str
    auton_start_sec: float
    auton_start_frame: int
    auton_stop_sec: float
    auton_stop_frame: int
    driver_start_sec: float
    driver_start_frame: int
    driver_stop_sec: float
    driver_stop_frame: int
    found_complete_match: bool
    notes: str | None
