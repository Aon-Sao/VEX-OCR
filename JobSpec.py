from pydantic import BaseModel


class JobSpec(BaseModel):
    class Division(BaseModel):
        event_sku: str
        program_code: str
        division_name: str

    src_file: str
    video_id: int
    divisions: list[Division]
    scan_start_offset: int = 0
