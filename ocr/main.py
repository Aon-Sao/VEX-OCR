import argparse
import msgspec
from pathlib import Path

from ocr.DataObjects import InputData
from ocr.MatchFinder import MatchFinder
from ocr.Config import CONFIG as config

import logging
log = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", required=True, type=Path)
    jsn_path = vars(parser.parse_args())["json"]
    with open(jsn_path, 'r') as fin:
        jsn = fin.read()
    return jsn

def run_ocr(input_json_str, vid_id = None):
    try:
        log_path = Path(f"video-{vid_id}.log") if vid_id else Path("ocrTool.log")
        logging.basicConfig(filename=log_path, level=logging.INFO)
        log.info(f"Started. Parsing input.")
        input_data = msgspec.json.decode(input_json_str, type=InputData)
        log.info(f"Configuring.")
        config.configure(input_data)
        log.info(f"Searching for matches.")
        MatchFinder().find_all_matches()
        log.info(f"DONE.")
    except Exception as e:
        return e