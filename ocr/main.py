import argparse

import msgspec
from pathlib import Path

from DataObjects import InputData
from MatchFinder import MatchFinder
from Config import CONFIG as config

import logging
log = logging.getLogger(__name__)
logging.basicConfig(filename="ocrTool.log", level=logging.INFO)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", required=True, type=Path)
    jsn_path = vars(parser.parse_args())["json"]
    with open(jsn_path, 'r') as fin:
        jsn = fin.read()
    return jsn

def main(input_json_str):
    log.info(f"Started. Parsing input.")
    input_data = msgspec.json.decode(input_json_str, type=InputData)
    log.info(f"Configuring.")
    config.configure(input_data)
    log.info(f"Searching for matches.")
    MatchFinder().find_all_matches()
    log.info(f"DONE.")


if __name__ == "__main__":
    main(input_json_str=parse_arguments())