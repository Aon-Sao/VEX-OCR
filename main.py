import json
from time import sleep

from video_copy_manager import VideoCopyManager

video_copy_manager = VideoCopyManager()

if __name__ == "__main__":
    config = json.load(open("config.json"))
    videos = config["videos"]

    for video in videos:
        f = video_copy_manager.add_job(video)

    # while True:
    #     sleep(30)