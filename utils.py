import cv2
from Frame import Frame
from config import CONFIG

def get_frame(video_pos, ocr = True):
    print(f"DEBUG: getting frame {video_pos.frame()}, OCR: {ocr}")
    CONFIG.video_obj.set(cv2.CAP_PROP_POS_FRAMES, video_pos.frame())
    _, frame = CONFIG.video_obj.read()
    return Frame(video_pos, frame, ocr=ocr)

def skip_search(frame_generator, accept=None, reject=None, ocr=True):
    # By default, we are looking for driver frames
    if accept is None:
        accept = lambda x: x.is_driver() and x.full_ocr
    # If there is no reject condition, don't halt early
    if reject is None:
        reject = lambda x: False

    # Do-While
    def do(pos):
        frame = get_frame(pos, ocr=ocr)
        if accept(frame):
            return "ACCEPT", frame
        elif reject(frame):
            return "REJECT", frame
        else:
            return "CONTINUE", frame
    pos = next(frame_generator)
    furthest_pos = pos
    msg = do(pos)
    while True:
        try:
            pos = frame_generator.send(msg)
            furthest_pos = max(furthest_pos, pos)
            msg = do(pos)
            if msg[0] == "ACCEPT":
                return msg[1], furthest_pos
            if msg[0] == "REJECT":
                break
        except StopIteration:
            return None, furthest_pos
    return None, furthest_pos

def highlight_region(img, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    cv2.rectangle(img, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (255, 0, 0), 5)
    return img