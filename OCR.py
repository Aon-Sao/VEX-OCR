from difflib import get_close_matches
from tempfile import TemporaryDirectory
from thefuzz import fuzz

import cv2
from config import CONFIG
import pytesseract

class Ocr:
    # Singleton
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = CONFIG.tesseract_path

    def interpret_results(self, raw_results, division_type="DEFAULT"):
        def longest_best_match(dct):
            score_sort = sorted(dct.items(), key=lambda x: x[1], reverse=True)
            best_score = score_sort[0][1]
            ties = filter(lambda x: x[1] >= best_score, score_sort)
            length_sort = sorted(ties, key=lambda x: len(x[0]), reverse=True)
            longest = length_sort[0][0]
            return longest

        def timer_str_to_sec(s):
            if ":" not in s:
                return False
            lst = s.split(":")
            if len(lst) > 2:
                return False
            minutes, seconds = lst
            if len(seconds) > 2:
                return False
            if not (minutes.isnumeric() and seconds.isnumeric()):
                return False
            if not (0 <= int(minutes) <= 59):
                return False
            if not (0 <= int(seconds) <= 59):
                return False
            return (int(minutes) * 60) + int(seconds)

        def cvt_nums(s):
            if _time := timer_str_to_sec(s):
                return _time
            elif s.isnumeric():
                return int(s)
            else:
                return False

        # Optional: Validate match category and extract number using regex derived therefrom
        match_num, div_name, match_timer, match_mode = raw_results.values()
        timer_secs = cvt_nums(match_timer)
        if not match_mode in CONFIG.expected_strings:
            match_mode = None
        ratios = {i: fuzz.partial_ratio(div_name.lower(), i) for i in CONFIG.division_names}
        div_name = longest_best_match(ratios)

        return timer_secs, match_num, match_mode, div_name

    def analyze_frame(self, img, division_type="DEFAULT"):
        gray = self.grayscale(img)
        regions = self.split_frame(gray, division_type=division_type)
        regions = [self.threshold(i) for i in regions]
        raw_results = self.ocr_batch(regions)
        return self.interpret_results(raw_results, division_type)

    def ocr_single(self, img):
        return pytesseract.image_to_string(img)

    def crop_image(self, img, y_start, y_stop, x_start, x_stop):
        return img[y_start:y_stop, x_start:x_stop]

    def split_frame(self, img, division_type="DEFAULT"):
        return [self.crop_image(img, *bounds) for bounds in CONFIG.ocr_regions[division_type].values()]

    def grayscale(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def threshold(self, img):
        return cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    def ocr_batch(self, images):
        with TemporaryDirectory() as tmpdir:
            i = 0
            for img in images:
                cv2.imwrite(f"{tmpdir}/img{i}.png", img)
                i += 1
            with open(f"{tmpdir}/batch.txt", 'w') as fout:
                fout.writelines([f"{tmpdir}/img{j}.png\n" for j in range(i)])

            results = pytesseract.image_to_string(f"{tmpdir}/batch.txt").split("\x0c")
            res_dct = dict()
            for region, raw in zip(CONFIG.ocr_regions.keys(), results):
                res_dct[region] = raw.strip()
            return res_dct

OCR = Ocr()
