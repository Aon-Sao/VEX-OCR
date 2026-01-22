import os
from collections import OrderedDict
from tkinter import filedialog
from tkinter import *
import cv2

class Config:
    # Singleton
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    #! Unhandled edge case: the sorting of the driver durations isn't also the sorting of the auton durations
    division_types = OrderedDict(sorted({
        "V5RC": {
            "DRIVER_DURATION": 105,
            "AUTON_DURATION": 15
        },
        "VURC": {
            "DRIVER_DURATION": 75,
            "AUTON_DURATION": 45
        },
        "VIQRC": {
            "DRIVER_DURATION": 60,
            "AUTON_DURATION": 0
        }}.items(), key=lambda d: d[1]["DRIVER_DURATION"]))
    ocr_regions = {
        "DEFAULT": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
            "MATCH_MODE": [0, 0, 0, 0],
        },
        "V5RC": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
        },
        "VURC": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
        },
        "VIQRC": {
            "MATCH_NUM": [0, 0, 0, 0],
            "DIVISION_NAME": [0, 0, 0, 0],
            "MATCH_TIMER": [0, 0, 0, 0],
        },
    }
    division_types_present = [
        "VIQRC",
    ]
    tesseract_path = "/usr/sbin/tesseract"
    video_path = None
    expected_strings = [
        "HS",
        "MS",
        "ES",
        "High",
        "Middle",
        "Elementary",
        "School",
        "Qual", "Qualification", "Qualifications",
        "Practice",
        "QF", "Quarterfinal", "Quarter-final",
        "SF", "Semifinal", "Semi-final",
        "F", "Final",
        "R16", "Round of 16", "Round-of-16",
        "R32", "Round of 16", "Round-of-32",
        "R64", "Round of 16", "Round-of-64",
        "R128", "Round of 16", "Round-of-128",
        "Skills",
        "Timeout",
        "Top",
        "Driver", "Driver Control"
        "Auton",
        "Autonomous",
        "Control"
    ]
    stream_id = -1
    division_id = -1
    division_names = ["Design Division"]
    event_skus = []

    def __init__(self):
        self.expected_strings.extend(self.division_names)
        self.expected_strings.extend(self.division_types_present)
        self.expected_strings = [i.lower() for i in self.expected_strings]

    def select_region(self, img, title="Select region"):
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        print(title)
        sel = [int(i) for i in cv2.selectROI(title, img)]
        return sel[1], sel[1] + sel[3], sel[0], sel[0] + sel[2]

    def select_ocr_regions(self, frame_num, division_type="DEFAULT"):
        for region in self.ocr_regions[division_type].keys():
            self.select_ocr_region(frame_num, division_type, region)

    def select_ocr_region(self, frame_num, division_type, field_type):
        assert division_type in self.ocr_regions.keys()
        vid = cv2.VideoCapture(self.video_path)
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = vid.read()
        title = f"Select {division_type} {field_type}"
        sel = self.select_region(frame, title)
        self.ocr_regions[division_type][field_type] = list(sel)
        cv2.destroyWindow(winname=title)

    def set_video_path(self, vid_path):
        self.video_path = vid_path

    def select_video_path(self):
        def browseFiles():
            self.video_path = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="Select video file",
                                                  filetypes=(("all files", "*.*"),),)
        # Create the root window
        window = Tk()

        # Set window title
        window.title('File Explorer')

        # Set window size
        window.geometry("500x500")

        # Set window background color
        window.config(background="black")

        # Create a File Explorer label
        label_file_explorer = Label(window,
                                    text="File Explorer using Tkinter",
                                    width=100, height=4,
                                    fg="green",
                                    bg="black")

        button_explore = Button(window,
                                text="Browse Files",
                                command=browseFiles,
                                fg="green",
                                bg="black")

        button_exit = Button(window,
                             text="Done",
                             command=exit,
                             fg="green",
                             bg="black")

        # Grid method is chosen for placing
        # the widgets at respective positions
        # in a table like structure by
        # specifying rows and columns
        label_file_explorer.grid(column=1, row=1)

        button_explore.grid(column=1, row=2)

        button_exit.grid(column=1, row=3)

        # Let the window wait for any events
        window.mainloop()

CONFIG = Config()