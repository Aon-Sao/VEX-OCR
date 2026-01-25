from typing import Optional

import msgspec

class Division(msgspec.Struct):
    program_code: str
    name: str
    event_sku: str
    division_id: int
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


class InputData(msgspec.Struct):
    pg_conn_str: str
    ssd_vid_path: str
    divisions: list[Division]
