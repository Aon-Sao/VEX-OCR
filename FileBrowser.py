from tkinter import filedialog
from tkinter import *


class FileBrowser:
    def __init__(self, title, start_dir):
        self.title = title
        self.start_dir = start_dir
        self.filename = None

    def browse(self):
        def browse_files():
            self.filename = filedialog.askopenfilename(
                initialdir=self.start_dir,
                title=self.title,
                filetypes=(("all files", "*.*"),), )

        # Create the root window
        window = Tk()
        window.title('File Browser')
        window.geometry("500x500")
        window.config(background="black")

        # Create a File Explorer label
        label_file_explorer = Label(window,
                                    text=self.title,
                                    width=100, height=4,
                                    fg="green",
                                    bg="black")

        button_explore = Button(window,
                                text="Browse Files",
                                command=browse_files,
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

        return self.filename