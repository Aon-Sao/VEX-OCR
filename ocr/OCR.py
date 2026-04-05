from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import pytesseract
from thefuzz import fuzz

from ocr.Config import CONFIG as config


class Ocr:

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
            if ":" in s and len(lst := s.split(":")) == 2:
                minutes, seconds = lst
                if (
                    (minutes + seconds).isnumeric()
                    and 0 <= int(minutes) <= 59
                    and 0 <= int(seconds) <= 59
                ):
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
        ratios = {
            i: fuzz.partial_ratio(div_name.lower(), i) for i in config.division_names
        }
        div_name = longest_best_match(ratios)
        div_type = [
            i.program_code for i in config.divisions if i.division_name == div_name
        ][0]
        return timer_secs, timer_str, match_num, match_mode, div_name, div_type

    @staticmethod
    def analyze_frame(img, video_pos):
        # cv2.imwrite(Path("./images") / f"{video_pos.frame()}-full.png", img)
        regions = Ocr.split_frame(img)
        regions = [Ocr.resize(i, 3) for i in regions]
        regions = [Ocr.grayscale(i) for i in regions]
        regions = [Ocr.threshold(i) for i in regions]
        # The documentation suggests a border size of 10 pixels
        regions = [Ocr.add_border(i, 10) for i in regions]
        # for index, region in enumerate(regions):
        #     cv2.imwrite(Path("./images") / f"{video_pos.frame()}-region_3x_{index}.png", region)

        raw_results = Ocr.ocr_batch(regions)
        # with open(Path("./images") / f"{video_pos.frame()}-ocr_res.txt", 'w') as fout:
        #     fout.writelines([f"{k}: {v}\n" for k, v in raw_results.items()])

        return Ocr.interpret_results(raw_results)

    @staticmethod
    def resize(img, factor):
        return cv2.resize(
            img, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC
        )

    @staticmethod
    def add_border(img, size: int):
        return cv2.copyMakeBorder(
            img, size, size, size, size, cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )

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
                fpath = Path(tmpdir) / f"img{i}.png"
                cv2.imwrite(fpath, img)
                i += 1
            with open(f"{tmpdir}/batch.txt", "w") as fout:
                fout.writelines([f"{tmpdir}/img{j}.png\n" for j in range(i)])
            tess_config = " ".join(
                ["--psm 7", "--user-patterns user-patterns" "--user-words user-words"]
            )
            results = pytesseract.image_to_string(
                f"{tmpdir}/batch.txt", config=tess_config
            ).split("\x0c")
            res_dct = dict()
            for region, raw in zip(config.ocr_regions.keys(), results):
                res_dct[region] = raw.strip()
            return res_dct
