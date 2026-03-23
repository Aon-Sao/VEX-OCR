from tempfile import TemporaryDirectory
from thefuzz import fuzz
from ocr.Config import CONFIG as config

import cv2

import pytesseract

class Ocr:
    # Singleton
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = config.tesseract_path

    @staticmethod
    def interpret_results(raw_results):
        def longest_best_match(dct):
            score_sort = sorted(dct.items(), key=lambda x: x[1], reverse=True)
            best_score = score_sort[0][1]
            ties = filter(lambda x: x[1] >= best_score, score_sort)
            length_sort = sorted(ties, key=lambda x: len(x[0]), reverse=True)
            longest = length_sort[0][0]
            return None if longest == "" else longest

        def timer_str_to_sec(s):
            if ":" in s and len(lst:=s.split(":")) == 2:
                minutes, seconds = lst
                if (minutes + seconds).isnumeric() and 0 <= int(minutes) <= 59 and 0 <= int(seconds) <= 59:
                    return (int(minutes) * 60) + int(seconds), f"{minutes}:{seconds}"
            return None, None

        match_num, div_name, match_timer, match_mode = raw_results.values()
        timer_secs, timer_str = timer_str_to_sec(match_timer)
        if "driver" in match_mode.lower():
            match_mode = "driver"
        elif "auton" in match_mode.lower():
            match_mode = "auton"
        else:
            match_mode = None
        if match_num == "":
            match_num = None
        # TODO: avoid special casing
        if match_num == "QUALS":
            match_num = "QUAL 5"
        ratios = {i: fuzz.partial_ratio(div_name.lower(), i) for i in config.division_names}
        div_name = longest_best_match(ratios)
        div_type = [i.program_code for i in config.divisions if i.division_name == div_name][0]
        return timer_secs, timer_str, match_num, match_mode, div_name, div_type

    @staticmethod
    def analyze_frame(img):
        gray = Ocr.grayscale(img)
        regions = Ocr.split_frame(gray)
        regions = [Ocr.threshold(i) for i in regions]
        regions = [Ocr.add_border(i, 20) for i in regions]
        raw_results = Ocr.ocr_batch(regions)
        return Ocr.interpret_results(raw_results)

    @staticmethod
    def add_border(img, size: int):
        return cv2.copyMakeBorder(img, size, size, size, size, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    @staticmethod
    def crop_image(img, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
        y_start = top_left_y
        y_stop = bottom_right_y
        x_start = top_left_x
        x_stop = bottom_right_x
        return img[y_start:y_stop, x_start:x_stop]

    @staticmethod
    def split_frame(img):
        return [Ocr.crop_image(img, *region) for region in config.ocr_regions.values()]

    @staticmethod
    def grayscale(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def threshold(img):
        return cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    @staticmethod
    def ocr_batch(images):
        with TemporaryDirectory() as tmpdir:
            i = 0
            for img in images:
                cv2.imwrite(f"{tmpdir}/img{i}.png", img)
                i += 1
            with open(f"{tmpdir}/batch.txt", 'w') as fout:
                fout.writelines([f"{tmpdir}/img{j}.png\n" for j in range(i)])

            results = pytesseract.image_to_string(f"{tmpdir}/batch.txt", config="--psm 7").split("\x0c")
            res_dct = dict()
            for region, raw in zip(config.ocr_regions.keys(), results):
                res_dct[region] = raw.strip()
            return res_dct