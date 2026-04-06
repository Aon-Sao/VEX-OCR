import cv2
import structlog

from ocr.Config import CONFIG as config
from ocr.FrameResolver import FrameResolver
from ocr.VideoPosition import VideoPosition

log = structlog.get_logger()

def get_frame(video_pos, ocr=True):
    config.video_obj.set(cv2.CAP_PROP_POS_FRAMES, video_pos.frame())
    _, frame = config.video_obj.read()
    return FrameResolver(video_pos, frame, ocr=ocr)


def skip_search(
    start, end, skip, accept=None, reject=None, ocr=True, left_to_right=True
):

    # Make sure types are correct
    start = VideoPosition(start)
    end = VideoPosition(end)
    skip = VideoPosition(skip)
    zero = VideoPosition(frame=0)

    if start == end:
        raise ValueError("Start and end position cannot be the same")
    if skip == zero:
        raise ValueError("Skip distance cannot be zero")

    if left_to_right:
        st = min(start, end)
        en = max(start, end) + 1
        sk = abs(skip)
    else:
        st = max(start, end)
        en = min(start, end) - 1
        sk = abs(skip) * -1

    log.debug(f"Searching from {st.frame()} to {en.frame()} with skip {sk.frame()}")

    frame_range = range(st.frame(), en.frame(), sk.frame())
    frame_range = [VideoPosition(frame=i) for i in frame_range]

    # By default, we are looking for driver frames
    if accept is None:
        accept = lambda x: x.is_driver() and x.full_ocr()
    # If there is no reject condition, don't halt early
    if reject is None:
        reject = lambda x: False

    furthest_pos = min(start, end)

    for pos in frame_range:
        frame = get_frame(pos, ocr=ocr)
        furthest_pos = max(furthest_pos, pos)
        if accept(frame):
            return frame, furthest_pos
        elif reject(frame):
            return None, furthest_pos
    log.debug("Reached end of search range")
    return None, furthest_pos
