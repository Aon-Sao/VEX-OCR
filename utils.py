from Frame import Frame
import cv2

def time_to_frame_num(fps, s):
    return int(s * fps)

def frame_num_to_time(fps, f):
    return f / fps

def is_driver_frame(frame):
    # Match mode says driver && timer is non-zero
    if not isinstance(frame.match_mode, str):
        return False
    return "driver".lower() in frame.match_mode.lower() \
        and frame.timer_seconds > 0

def is_auton_frame(frame):
    # Match mode says auton && timer is non-zero
    if not isinstance(frame.match_mode, str):
        return False
    return "auton".lower() in frame.match_mode.lower() \
        and frame.timer_seconds > 0

def get_frame(video, frame_num, ocr = True):
    print(f"DEBUG: getting frame {frame_num}, OCR: {ocr}")
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = video.read()
    return Frame(frame_num, frame, ocr=ocr)

def select_region(img, title="Select region"):
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    print(title)
    sel = [int(i) for i in cv2.selectROI(title, img)]
    return sel[1], sel[1] + sel[3], sel[0], sel[0] + sel[2]
