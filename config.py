from collections import OrderedDict
#! Unhandled edge case: the sorting of the driver durations isn't also the sorting of the auton durations
DIVISION_TYPES = {
    "V5RC": {
        "DRIVER_DURATION": 105,
        "AUTON_DURATION": 15
    },
    "VURC": {
        "DRIVER_DURATION": 75,
        "AUTON_DURATION": 45
    },
    "VIQRC": {
        "DRIVER_DURATION": 60,
        "AUTON_DURATION": 0
    }
}
DIVISION_TYPES = OrderedDict(sorted(DIVISION_TYPES.items(), key=lambda d: d[1]["DRIVER_DURATION"]))
STREAM_ID = -1
DIVISION_ID = -1
DIVISION_NAME_REGEX = fr".*"
DIVISIONS_PRESENT = []
EVENT_SKUS = []
VIDEO_PATH = "some_video"