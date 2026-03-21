import argparse
import json

import msgspec
from pathlib import Path

from DataObjects import InputData
from MatchFinder import MatchFinder
from Config import CONFIG as config


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", required=True, type=Path)
    jsn_path = vars(parser.parse_args())["json"]
    with open(jsn_path, 'r') as fin:
        jsn = fin.read()
    return jsn

def main(input_json_str):
    input_data = msgspec.json.decode(input_json_str, type=InputData)
    config.configure(input_data)
    MatchFinder().find_all_matches()


if __name__ == "__main__":
    main(input_json_str=parse_arguments())