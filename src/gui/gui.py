from tkinter import *
from tkinter import messagebox

class GuiAdmin:
    root = Tk()
    root.title('MQTT Client')
    frame : Frame # declared locally to thee clase to be called in other functions besides constructor

    def __init__(self):
        self.root.geometry("640x480")
        self.frame = Frame(self.root, width=640, height=512, relief='raised')
        
        # Username entry + label
        Label(self.frame, text="Nume utilizator",font="arial",padx=5,pady=5).pack()
        self.name_entry=Entry(self.frame,width=40)
        self.name_entry.focus()
        self.name_entry.pack()

        # Password entry + label
        Label(self.frame, text="Parola",font="arial",padx=5,pady=5).pack()
        self.password_entry=Entry(self.frame,width=40)
        self.password_entry.pack()

        # Submit button
        self.submit_button=Button(self.frame,text="Submit",font="arial",command=self.submit)
        self.submit_button.pack()
        self.frame.pack()
    
    def get_name(self):
        return self.name_entry.get()
    
    def get_password(self):
        return self.password_entry.get()

    def submit(self):
        self.name_entry.get()
        self.password_entry.get()
        if(len(self.get_name())!=0 and len(self.get_password())!=0):
            print(self.name_entry.get()+"/"+self.password_entry.get())
            self.frame.destroy()
            p_s=Pub_Sub()
            
class Pub_Sub(GuiAdmin):
    def __init__(self):
        self.frame=Frame(self.root,width=640, height=512, relief='raised')
        Button(self.frame,text="Publish",font="arial",command=self.publish).pack()
        Button(self.frame,text="Subscribe",font="arial",command=self.subscribe).pack() 

        self.frame.pack()
    
    def publish(self):
        self.frame.destroy()
        print("publish")
        Publish()

    def subscribe(self):
        self.frame.destroy()
        print("subscribe")
        Subscribe()
    

class Subscribe(GuiAdmin):
    def __init__(self):
        self.frame=Frame(self.root,width=640, height=512, relief='raised')
        
        # Client label + entry box
        Label(self.frame,text="Nume",font="arial",padx=5,pady=5).pack()
        self.subscriber_entry_name=Entry(self.frame,width=40)
        self.subscriber_entry_name.pack()

        # Topic label + topic text box
        Label(self.frame,text="Topicuri",font="arial",padx=5,pady=5).pack()
        self.subscribe_topics=Text(self.frame,width=40,height=15)
        self.subscribe_topics.pack()

        # Keep alive
        Label(self.frame,text="Keep Alive",font="arial",padx=5,pady=5).pack()
        self.subscribe_keep_alive=IntVar()
        self.subscribe_keep_alive=Entry(self.frame,width=40)
        self.subscribe_keep_alive.pack()

        # QOS
        Label(self.frame, text='QoS',font='arial').pack()
        self.QoS=StringVar()
        Radiobutton(self.frame, text='QoS 1',value=1,variable=self.QoS).pack()
        Radiobutton(self.frame, text='QoS 2',value=2,variable=self.QoS).pack()
        Radiobutton(self.frame, text='QoS 3',value=3,variable=self.QoS).pack()
        
        # Subscribe Button

        self.sub=Button(self.frame,text="Subscribe",font="arial",command=self.submit)
        self.sub.pack()

        # Go to the Pub/Sub select page
        self.last=Button(self.frame,text="GO BACK",font="arial",command=self.last_page)
        self.last.pack()


        self.frame.pack()
    
    def last_page(self):
        self.frame.destroy()
        Pub_Sub()

    def submit(self):
        if(len(self.subscriber_entry_name.get())!=0 and self.QoS!=0 and self.subscribe_keep_alive!=0):
            print("numele subscriberului: "+self.subscriber_entry_name.get()+"\nLista de topicuri la care acesta s-a abonat:\n"+self.subscribe_topics.get(1.0,END)+"\nQoS-ul topicurilor:"+self.QoS.get()+"\nKeep Alive:"+self.subscribe_keep_alive.get())
        

class Publish(GuiAdmin):
    def __init__(self):
        self.frame=Frame(self.root,width=640, height=512, relief='raised')
        
        # Client label + entry box
        Label(self.frame, text="Nume",font="arial",padx=5,pady=5).pack()
        self.publisher_entry_name=Entry(self.frame,width=40)
        self.publisher_entry_name.pack()

        # Topic label + topic text box
        Label(self.frame,text="Topicuri",font="arial",padx=5,pady=5).pack()
        self.publisher_topics=Entry(self.frame,width=40)
        self.publisher_topics.pack()

         # Payload label + entry
        Label(self.frame,text="Payload",font="arial",padx=5,pady=5).pack()
        self.publisher_payload=Entry(self.frame,width=40)
        self.publisher_payload.pack()

        # Keep alive
        Label(self.frame,text="Keep Alive",font="arial",padx=5,pady=5).pack()
        self.publisher_keep_alive=IntVar()
        self.publisher_keep_alive=Entry(self.frame,width=40)
        self.publisher_keep_alive.pack()

        # QOS
        Label(self.frame, text='QoS',font='arial').pack()
        self.QoS=StringVar()
        Radiobutton(self.frame, text='QoS 1',value=1,variable=self.QoS).pack()
        Radiobutton(self.frame, text='QoS 2',value=2,variable=self.QoS).pack()
        Radiobutton(self.frame, text='QoS 3',value=3,variable=self.QoS).pack()
        
        self.pub=Button(self.frame,text="Publish",font="arial",command=self.submit)
        self.pub.pack()

        # Go to the Pub/Sub select page
        self.last=Button(self.frame,text="GO BACK",font="arial",command=self.last_page)
        self.last.pack()

        self.frame.pack()

    def last_page(self):
        self.frame.destroy()
        Pub_Sub()
    
    def submit(self):
        if(len(self.publisher_entry_name.get())!=0 ):
            print("numele publisher-ului: "+self.publisher_entry_name.get()+"\nTopicul postat:\n"+self.publisher_topics.get()+"\nQoS-ul topicului:"+self.QoS.get()+"\nKeep Alive:"+self.publisher_keep_alive.get()+"\nPayload: "+self.publisher_payload.get())
        
        


if __name__ == "__main__":
    gui = GuiAdmin()
    gui.root.mainloop() # runs the gui in loop
