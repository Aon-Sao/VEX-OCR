from subprocess import run
import functools
import cv2
from FrameResolver import FrameResolver

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

def send_match(match):
    # For now, just display them
    print(match)

def get_frame(config, video_pos, ocr = True):
    # print(f"DEBUG: getting frame {video_pos.frame()}")
    config.video_obj.set(cv2.CAP_PROP_POS_FRAMES, video_pos.frame())
    _, frame = config.video_obj.read()
    return FrameResolver(config, video_pos, frame, ocr=ocr)

def display_img(img):
    cv2.namedWindow("display", cv2.WINDOW_NORMAL)
    cv2.imshow("display", img)
    cv2.waitKey(0)
    cv2.destroyWindow("display")

def skip_search(config, frame_generator, accept=None, reject=None, ocr=True):
    # By default, we are looking for driver frames
    if accept is None:
        accept = lambda x: (x.is_driver() or x.is_auton()) and x.full_ocr()
    # If there is no reject condition, don't halt early
    if reject is None:
        reject = lambda x: False

    # Do-While
    def do(pos):
        frame = get_frame(config, pos, ocr=ocr)
        # display_img(frame.cv2_frame)
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
            if msg[0] == "ACCEPT":
                return msg[1], furthest_pos
            if msg[0] == "REJECT":
                break
            if msg[0] == "CONTINUE":
                pos = frame_generator.send(msg)
                furthest_pos = max(furthest_pos, pos)
                msg = do(pos)
        except StopIteration:
            return None, furthest_pos
    return None, furthest_pos

def highlight_region(img, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    cv2.rectangle(img, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (255, 0, 0), 5)
    return img