from tkinter import *
from tkinter import messagebox

class GuiAdmin:
    root = Tk()
    root.title('MQTT Client')
    frame : Frame # declared locally to thee clase to be called in other functions besides constructor

    def __init__(self):
        self.frame = Frame(self.root, width=640, height=512, relief='raised')
        label = Label(self.frame, text="Enter credentials:", bg="grey")
        label.place(relx=0.5, rely=0.14, anchor=CENTER)
        user_label = Label(self.frame, text=" user:", bg="grey")
        user_label.place(relx=0.37, rely=0.2, anchor=CENTER)
        user_entry = Entry(self.frame)
        user_entry.place(relx=0.5, rely=0.2, anchor=CENTER)
        password_label = Label(self.frame, text="Password:", bg="grey")
        password_label.place(relx=0.35, rely=0.26, anchor=CENTER)
        password_entry = Entry(self.frame, show="*")
        password_entry.place(relx=0.5, rely=0.26, anchor=CENTER)
        self.frame.pack()
        buttonSpotify = Button(self.frame, text=' Submit ', fg='black', bg='white',
                                        command=lambda: self.verify_login_input(user_entry.get(), password_entry.get()),
                                        height=1, width=7) # on click it resets the frame if the credentials are valid
        buttonSpotify.place(relx=0.5, rely=0.32, anchor=CENTER)

    def verify_login_input(self,user,password):
        if  user == "root" and password == "pass":
            self.frame.destroy()
            self.frame = Frame(self.root, width=640, height=512, relief='raised')
            label = Label(self.frame, text="to be continued", bg="grey")
            label.place(relx=0.5, rely=0.14, anchor=CENTER)
            self.frame.pack()
        else:
            messagebox.showinfo("Error", "Wrong credentials") # prints if credentials are wrong

if __name__ == "__main__":
    gui = GuiAdmin()
    gui.root.mainloop() # runs the gui in loop
