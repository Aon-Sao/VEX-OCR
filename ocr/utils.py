from subprocess import run
import functools
import cv2

from ocr.FrameResolver import FrameResolver
from ocr.Config import CONFIG as config
from ocr.VideoPosition import VideoPosition


def notify(dest):
    def wrapper_maker(func):
        @functools.wraps(func)
        def wrapper():
            message = "No message"
            try:
                result = func()
                message = "SUCCESS"
                return result
            except Exception as e:
                message = f"{type(e).__name__}: {e}"
                raise e
            finally:
                run(["curl", "-d", f'"{message}"', f"ntfy.sh/{dest}"], capture_output=True)
        return wrapper
    return wrapper_maker

def get_frame(video_pos, ocr = True):
    config.video_obj.set(cv2.CAP_PROP_POS_FRAMES, video_pos.frame())
    _, frame = config.video_obj.read()
    return FrameResolver(video_pos, frame, ocr=ocr)

def display_img(img):
    cv2.namedWindow("display", cv2.WINDOW_NORMAL)
    cv2.imshow("display", img)
    cv2.waitKey(0)
    cv2.destroyWindow("display")

def skip_search(start, end, skip, accept=None, reject=None, ocr=True):

    # Make sure types are correct
    start = VideoPosition(start)
    end = VideoPosition(end)
    skip = VideoPosition(skip)
    zero = VideoPosition(frame=0)

    # Handle potentially naive use
    if (start < end) and (skip > zero):
        frame_range = range(start.frame(), end.frame(), skip.frame())
    elif (start > end) and (skip > zero):
        frame_range = range(end.frame(), start.frame(), skip.frame() * -1)
    elif (start < end) and (skip < zero):
        frame_range = range(end.frame(), start.frame(), skip.frame())
    elif (start > end) and (skip < zero):
        frame_range = range(start.frame(), end.frame(), skip.frame() * -1)
    elif start == end:
        raise ValueError("Start and end position cannot be the same")
    elif skip == zero:
        raise ValueError("Skip distance cannot be zero")
    else:
        raise Exception("How did we get here...")
    frame_range = [VideoPosition(frame=i) for i in frame_range]

    # By default, we are looking for driver frames
    if accept is None:
        accept = lambda x: x.is_driver() and x.full_ocr()
    # If there is no reject condition, don't halt early
    if reject is None:
        reject = lambda x: False

    furthest_pos = max(start, end)

    for pos in frame_range:
        frame = get_frame(pos, ocr=ocr)
        if accept(frame):
            return frame, furthest_pos
        elif reject(frame):
            return None, furthest_pos
        furthest_pos = max(furthest_pos, pos)
    return None, furthest_pos

def highlight_region(img, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    cv2.rectangle(img, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (255, 0, 0), 5)
    return img

