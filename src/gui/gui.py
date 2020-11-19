from tkinter import *
from tkinter import messagebox

class GuiAdmin:
    root = Tk()
    root.title('MQTT Client')
    frame : Frame # declared locally to thee clase to be called in other functions besides constructor

    def __init__(self):
        self.frame = Frame(self.root, width=640, height=512, relief='raised')

if __name__ == "__main__":
    gui = GuiAdmin()
    gui.root.mainloop() # runs the gui in loop
