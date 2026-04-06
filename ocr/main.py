import msgspec
import structlog

from ocr.Config import CONFIG as config
from ocr.DataObjects import InputData
from ocr.MatchFinder import MatchFinder

log: structlog.BoundLogger = None


def setup_logging(vid_id: int):
    global log
    structlog.configure(processors=[
        # structlog.processors.TimeStamper,
        # structlog.processors.dict_tracebacks,
        structlog.dev.ConsoleRenderer()
    ])
    log = structlog.get_logger()
    log.bind(vid_id=vid_id)
    return log


def run_ocr(input_json_str, vid_id):
    try:
        setup_logging(vid_id)
        input_data = msgspec.json.decode(input_json_str, type=InputData)
        log.info("OCR started", input_data=input_data)
        config.configure(input_data)
        config.open_video()
        MatchFinder().find_all_matches()
        config.release_video()
        log.info("OCR Done")
        return True
    except Exception as e:
        log.error(f"Exception while trying to OCR", exc_info=e)
        return False
