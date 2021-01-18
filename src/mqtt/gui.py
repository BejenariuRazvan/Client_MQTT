from tkinter import *
from tkinter import ttk
from MQTT_client import *

class Gui:
    root =Tk()
    root.title('MQTT Client')
    frame : Frame # declared locally to thee clase to be called in other functions besides constructor
    
    def __init__(self):
        self.root.geometry('640x480')
        self.frame = Frame(self.root, width=640, height=512, relief='raised')
        
         # Username entry + label
        Label(self.frame, text="Nume utilizator",font="arial",padx=5,pady=5).pack()
        self.name_entry=Entry(self.frame,width=40)
        self.name_entry.focus()
        self.name_entry.pack()

         # Password entry + label
        Label(self.frame, text="Parola",font="arial",padx=5,pady=5).pack()
        self.password_entry=Entry(self.frame,width=40,show='*')
        self.password_entry.pack()

        # Submit button
        self.submit_button=Button(self.frame,text="Connect",font="arial",command=self.submit)
        self.submit_button.pack()
        self.frame.pack()

    def submit(self):
        if(len(self.name_entry.get())!=0 and len(self.password_entry.get())!=0):
            print("nume conectare: "+self.name_entry.get()+"\nParola conectare: "+self.password_entry.get())
            self.nume=self.name_entry.get()
            self.parola=self.password_entry.get()
            self.frame.destroy()
            Pub_Sub()


class Pub_Sub(Gui):
    notebook : ttk.Notebook
    def __init__(self):
        self.frame=Frame(self.root,width=640, height=512, relief='raised')
        self.notebook=ttk.Notebook(self.frame)
        self.publish_frame=Frame(self.notebook)
        self.subscribe_frame=Frame(self.notebook)
        self.notebook.add(self.publish_frame,text='Publish')
        self.SUB()
        self.PUB()
        self.notebook.add(self.subscribe_frame,text='Subscribe')
        self.notebook.pack()
        self.frame.pack()
    
    def SUB(self):
        Label(self.subscribe_frame,text="Nume",font="arial",padx=5,pady=5).pack()
        self.subscriber_entry_name=Entry(self.subscribe_frame,width=40)
        self.subscriber_entry_name.pack()

        # Topic label + topic text box
        Label(self.subscribe_frame,text="Topicuri",font="arial",padx=5,pady=5).pack()
        self.subscribe_topics=Text(self.subscribe_frame,width=40,height=10)
        self.subscribe_topics.pack()

        # Keep alive
        Label(self.subscribe_frame,text="Keep Alive",font="arial",padx=5,pady=5).pack()
        self.subscribe_keep_alive=IntVar()
        self.subscribe_keep_alive=Entry(self.subscribe_frame,width=40)
        self.subscribe_keep_alive.pack()

        # QOS
        Label(self.subscribe_frame, text='QoS',font='arial').pack()
        self.QoS=IntVar()
        Radiobutton(self.subscribe_frame, text='QoS 0',value=0,variable=self.QoS).pack()
        Radiobutton(self.subscribe_frame, text='QoS 1',value=1,variable=self.QoS).pack()
        Radiobutton(self.subscribe_frame, text='QoS 2',value=2,variable=self.QoS).pack()
            
        # Subscribe Button

        self.sub=Button(self.subscribe_frame,text="Subscribe",font="arial",command=self.submit_subscribe)
        self.sub.pack()

        self.frame.pack()
        

    def submit_subscribe(self):
        if(len(self.subscriber_entry_name.get())!=0 and self.QoS!=0 and self.subscribe_keep_alive!=0):
            #print("numele subscriberului: "+self.subscriber_entry_name.get()+"\nLista de topicuri la care acesta s-a abonat:\n"+self.subscribe_topics.get(1.0,END)+"\nQoS-ul topicurilor:"+self.QoS.get()+"\nKeep Alive:"+self.subscribe_keep_alive.get())
            print(type(int(self.subscribe_keep_alive.get())))
            subscriber = MQTTSubscriber(IP_, PORT,self.subscriber_entry_name.get() , [self.subscribe_topics.get(1.0,END)], int(self.subscribe_keep_alive.get()), self.QoS.get())

    def PUB(self):
        # Client label + entry box
        Label(self.publish_frame, text="Nume",font="arial",padx=5,pady=5).pack()
        self.publisher_entry_name=Entry(self.publish_frame,width=40)
        self.publisher_entry_name.pack()

        # Topic label + topic text box
        Label(self.publish_frame,text="Topicuri",font="arial",padx=5,pady=5).pack()
        self.publisher_topics=Entry(self.publish_frame,width=40)
        self.publisher_topics.pack()

         # Payload label + entry
        Label(self.publish_frame,text="Payload",font="arial",padx=5,pady=5).pack()
        self.publisher_payload=Entry(self.publish_frame,width=40)
        self.publisher_payload.pack()

        # Keep alive
        Label(self.publish_frame,text="Keep Alive",font="arial",padx=5,pady=5).pack()
        self.publisher_keep_alive=IntVar()
        self.publisher_keep_alive=Entry(self.publish_frame,width=40)
        self.publisher_keep_alive.pack()
        
        # QOS
        Label(self.publish_frame, text='QoS',font='arial').pack()
        self.QoS=IntVar()
        Radiobutton(self.publish_frame, text='QoS 0',value=0,variable=self.QoS).pack()
        Radiobutton(self.publish_frame, text='QoS 1',value=1,variable=self.QoS).pack()
        Radiobutton(self.publish_frame, text='QoS 2',value=2,variable=self.QoS).pack()
        
        # Publish type
        Label(self.publish_frame, text='Publish type',font='arial').pack()
        self.publish_type=IntVar()
        Radiobutton(self.publish_frame, text='Manual',value=1,variable=self.publish_type).pack()
        Radiobutton(self.publish_frame, text='Automat',value=2,variable=self.publish_type).pack()
        
        self.check=Button(self.publish_frame,text="Check interval",font="arial",command=self.get_type)
        self.check.pack()

        
        Label(self.publish_frame,text="publish interval",font="arial",padx=5,pady=5).pack()
        self.publisher_time_interval=Entry(self.publish_frame,width=40,state=DISABLED)
        self.publisher_time_interval.pack()



        self.pub=Button(self.publish_frame,text="Publish",font="arial",command=self.submit_publish)
        self.pub.pack()

        self.frame.pack()
    
    def get_type(self):
        if(self.publish_type.get()==2):
            self.publisher_time_interval.config(state=NORMAL)
        else:
            self.publisher_time_interval.config(state=DISABLED)


    def submit_publish(self):
        if(len(self.publisher_entry_name.get())!=0 ):
            # print("numele publisher-ului: "+self.publisher_entry_name.get()+"\nTopicul postat:\n"+self.publisher_topics.get()+"\nQoS-ul topicului:"+self.QoS.get()+"\nKeep Alive:"+self.publisher_keep_alive.get()+"\nPayload: "+self.publisher_payload.get())
            publisher = MQTTPublisher(IP_, PORT, self.publisher_entry_name.get(),self.publisher_topics.get(),self.publisher_payload.get(), int(self.publisher_keep_alive.get()), int(self.QoS.get()),self.publish_type.get(),int(self.publisher_time_interval.get()))
             



if __name__ == "__main__":
    gui = Gui()
    gui.root.mainloop() # runs the gui in loop
