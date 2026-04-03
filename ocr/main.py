import argparse
import sys

import msgspec
from pathlib import Path

from ocr.DataObjects import InputData
from ocr.MatchFinder import MatchFinder
from ocr.Config import CONFIG as config

import logging

log = logging.getLogger(__name__)


def setup_logging(vid_id: int):
    log_path = Path(f"video-{vid_id}.log") if vid_id else Path("ocrTool.log")

    file_handler = logging.FileHandler(log_path)
    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[file_handler, console_handler]
    )

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical(f"Uncaught exception in vid_id: {vid_id}", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def run_ocr(input_json_str, vid_id=None):
    try:
        print(f"run_ocr vid_id: {vid_id}")
        setup_logging(vid_id)
        log.info("Started. Parsing input. vid_id: %s input_json_str: %s", vid_id, input_json_str)
        input_data = msgspec.json.decode(input_json_str, type=InputData)
        log.info("Configuring.")
        config.configure(input_data)
        config.open_video()
        log.info("Searching for matches.")
        MatchFinder().find_all_matches()
        log.info("Releasing hardware & files")
        config.release_video()
        log.info("DONE.")
        return True
    except Exception as e:
        log.exception(f"Error in vid_id: {vid_id}, Error: {e}")
        return e
