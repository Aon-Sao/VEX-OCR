import json
from time import sleep
from dotenv import load_dotenv
from video_copy_manager import VideoCopyManager

load_dotenv()

if __name__ == "__main__":
    video_copy_manager = VideoCopyManager()
    config = json.load(open("config.json"))
    videos = config["videos"]

    for video in videos:
        f = video_copy_manager.add_job(video)
        f.result()

    # while True:
    #     sleep(30)
