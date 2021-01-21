import logging
import socket
import re
from threading import Thread
from time import sleep
from tkinter.scrolledtext import ScrolledText
from control_packets import *
from datetime import datetime
from random import randint
from tkinter import *
from tkinter import ttk
from system_info import *

IP_ = '127.0.0.1'
PORT = 1883
g_generated_client_id = 0
g_manual_publish_flag = 0


class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.DEBUG)
        self.widget = widget
        self.widget.config(state='disabled')
        self.widget.tag_config("INFO", foreground="black")
        self.widget.tag_config("DEBUG", foreground="grey")
        self.widget.tag_config("WARNING", foreground="orange")
        self.widget.tag_config("ERROR", foreground="red")
        self.widget.tag_config("CRITICAL", foreground="red", underline=1)
        self.red = self.widget.tag_configure("red", foreground="red")

    def emit(self, record):
        self.widget.config(state='normal')
        # Append message (record) to the widget
        self.widget.insert(END, record.asctime + ": " + self.format(record) + '\n', record.levelname)
        self.widget.see(END)  # Scroll to the bottom
        self.widget.config(state='disabled')
        self.widget.update()  # Refresh the widget


class Gui:
    root = Tk()
    root.title('MQTT Client')
    frame: Frame  # declared locally to thee clase to be called in other functions besides constructor

    def __init__(self):
        self.root.geometry('640x700')
        self.frame = Frame(self.root, width=640, height=512, relief='raised')

        # Username entry + label
        Label(self.frame, text="Name", font="arial", padx=5, pady=5).pack()
        self.name_entry = Entry(self.frame, width=40)
        self.name_entry.focus()
        self.name_entry.pack()

        # Password entry + label
        Label(self.frame, text="Password", font="arial", padx=5, pady=5).pack()
        self.password_entry = Entry(self.frame, width=40, show="*")
        self.password_entry.pack()

        # Submit button
        self.submit_button = Button(self.frame, text="Connect", font="arial", command=self.submit)
        self.submit_button.pack()

        Label(self.frame, text="Don't have an account?", font="arial", padx=5, pady=5).pack()
        self.registration_button = Button(self.frame, text="Register", font="arial", command=self.register)
        self.registration_button.pack()

        self.user_name = ""
        self.password = ""
        self.publisher = None
        self.subscriber = None
        self.notebook = None
        self.publish_frame = None
        self.subscribe_frame = None
        self.subscriber_entry_name = None
        self.subscribe_topics = None
        self.subscribe_keep_alive = None
        self.QoS = None
        self.logger = None
        self.publisher_entry_name = None
        self.publisher_topics = None
        self.publisher_payload = None
        self.publisher_keep_alive = None
        self.publish_type = None
        self.check = None
        self.publisher_time_interval = None
        self.pub = None

        self.frame.pack()

    def register(self):
        f = open("clienti.txt", "a+")
        f.write(str(self.name_entry.get()) + ":" + str(self.password_entry.get()) + "\n")
        self.name_entry.delete(0, END)
        self.password_entry.delete(0, END)
        f.close()

    def submit(self):
        f = open("clienti.txt", "r")
        t = f.readlines()
        ok = 0
        for pers in t:
            n = ""
            i = 0
            while pers[i] != ":":
                n = n + pers[i]
                i = i + 1
            i = i + 1
            p = pers[i:-1]
            if self.name_entry.get() == n and self.password_entry.get() == p:
                self.user_name = self.name_entry.get()
                self.password = self.password_entry.get()
                self.frame.destroy()
                ok = 1
                self.create_pub_sub_gui()
                break
        if ok == 0:
            Label(self.frame, text="Name or password incorrect").pack()
        f.close()

    def create_pub_sub_gui(self):
        self.frame = Frame(self.root, width=640, height=512, relief='raised')
        self.notebook = ttk.Notebook(self.frame)
        self.publish_frame = Frame(self.notebook)
        self.subscribe_frame = Frame(self.notebook)
        self.notebook.add(self.publish_frame, text='Publish')
        self.create_subscriber()
        self.create_publisher()
        self.notebook.add(self.subscribe_frame, text='Subscribe')
        self.notebook.pack()
        # Add text widget to display logging info
        self.logger = ScrolledText(self.root, state='disabled')
        self.logger.configure(font='TkFixedFont')
        # Create textLogger
        text_handler = WidgetLogger(self.logger)
        # Logging configuration
        logging.basicConfig(filename='test.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)
        self.logger.pack()
        self.frame.pack()

    def create_subscriber(self):
        Label(self.subscribe_frame, text="Name", font="arial", padx=5, pady=5).pack()
        self.subscriber_entry_name = Entry(self.subscribe_frame, width=40)
        self.subscriber_entry_name.pack()

        # Topic label + topic text box
        Label(self.subscribe_frame, text="Topics", font="arial", padx=5, pady=5).pack()
        self.subscribe_topics = Text(self.subscribe_frame, width=40, height=10)
        self.subscribe_topics.pack()

        # Keep alive
        Label(self.subscribe_frame, text="Keep Alive", font="arial", padx=5, pady=5).pack()
        self.subscribe_keep_alive = IntVar()
        self.subscribe_keep_alive = Entry(self.subscribe_frame, width=40)
        self.subscribe_keep_alive.pack()

        # QOS
        Label(self.subscribe_frame, text='QoS', font='arial').pack()
        self.QoS = IntVar()
        Radiobutton(self.subscribe_frame, text='QoS 0', value=0, variable=self.QoS).pack()
        Radiobutton(self.subscribe_frame, text='QoS 1', value=1, variable=self.QoS).pack()
        Radiobutton(self.subscribe_frame, text='QoS 2', value=2, variable=self.QoS).pack()
        # Subscribe Button

        self.sub = Button(self.subscribe_frame, text="Subscribe", font="arial", command=self.submit_subscribe)
        self.sub.pack()
        self.frame.pack()

    def submit_subscribe(self):
        topic_list = self.subscribe_topics.get(1.0, END).split("\n")
        topic_list.pop()
        if len(self.subscriber_entry_name.get()) != 0 and len(self.subscribe_topics.get(1.0, END)) != 0 \
                and len(self.subscribe_keep_alive.get()) != 0 and re.match("^[0-9]*$", self.subscribe_keep_alive.get()):
            if self.subscriber is None:
                self.subscriber = MQTTSubscriber(IP_, PORT, self.user_name, self.password,
                                                 self.subscriber_entry_name.get(),
                                                 topic_list, int(self.subscribe_keep_alive.get()),
                                                 self.QoS.get())
        else:
            logging.error("Invalid information entered.")

    def create_publisher(self):
        # Client label + entry box
        Label(self.publish_frame, text="Name", font="arial", padx=5, pady=5).pack()
        self.publisher_entry_name = Entry(self.publish_frame, width=40)
        self.publisher_entry_name.pack()

        # Topic label + topic text box
        Label(self.publish_frame, text="Topics", font="arial", padx=5, pady=5).pack()
        self.publisher_topics = ttk.Combobox(self.publish_frame, values=["CPU", "CPU Loads", "Cpu Temps",
                                                                         "Memory", "Disk", "Network"])
        self.publisher_topics.pack()
        self.publisher_topics.current(0)

        # Payload label + entry
        # Label(self.publish_frame, text="Payload", font="arial", padx=5, pady=5).pack()
        # self.publisher_payload = Entry(self.publish_frame, width=40)
        # self.publisher_payload.pack()

        # Keep alive
        Label(self.publish_frame, text="Keep Alive", font="arial", padx=5, pady=5).pack()
        self.publisher_keep_alive = IntVar()
        self.publisher_keep_alive = Entry(self.publish_frame, width=40)
        self.publisher_keep_alive.pack()

        # QOS
        Label(self.publish_frame, text='QoS', font='arial').pack()
        self.QoS = IntVar()
        Radiobutton(self.publish_frame, text='QoS 0', value=0, variable=self.QoS).pack()
        Radiobutton(self.publish_frame, text='QoS 1', value=1, variable=self.QoS).pack()
        Radiobutton(self.publish_frame, text='QoS 2', value=2, variable=self.QoS).pack()

        # Publish type
        Label(self.publish_frame, text='Publish type', font='arial').pack()
        self.publish_type = IntVar()
        Radiobutton(self.publish_frame, text='Manual', value=1, variable=self.publish_type).pack()
        Radiobutton(self.publish_frame, text='Automat', value=2, variable=self.publish_type).pack()

        self.check = Button(self.publish_frame, text="Check interval", font="arial", command=self.get_type)
        self.check.pack()

        Label(self.publish_frame, text="Publish Interval", font="arial", padx=5, pady=5).pack()
        self.publisher_time_interval = Entry(self.publish_frame, width=40, state=DISABLED)
        self.publisher_time_interval.pack()

        self.pub = Button(self.publish_frame, text="Publish", font="arial", command=self.submit_publish)
        self.pub.pack()
        self.frame.pack()

    def get_type(self):
        if self.publish_type.get() == 2:
            self.publisher_time_interval.config(state=NORMAL)
        else:
            self.publisher_time_interval.config(state=DISABLED)

    def submit_publish(self):
        global g_manual_publish_flag
        print(self.QoS.get())
        if len(self.publisher_entry_name.get()) != 0 and re.match("[0-9]*$", self.publisher_keep_alive.get()) \
                and len(self.publisher_keep_alive.get()) != 0:
            publish_interval = 0
            if self.publisher_time_interval.get():
                publish_interval = int(self.publisher_time_interval.get())
            if self.publisher is None:
                self.publisher_payload = self.publisher_topics.get()
                self.publisher = MQTTPublisher(IP_, PORT, self.user_name, self.password,
                                               self.publisher_entry_name.get(), self.publisher_topics.get(),
                                               int(self.publisher_keep_alive.get()),
                                               int(self.QoS.get()), self.publish_type.get(),
                                               publish_interval)
            if self.publish_type.get() == 2:
                for element in self.publish_frame.pack_slaves():
                    element.config(state=DISABLED)
            if self.publish_type.get() == 1:
                for element in self.publish_frame.pack_slaves():
                    element.config(state=DISABLED)
                self.pub.config(state=NORMAL)
                g_manual_publish_flag += 1
        else:
            logging.error("Invalid information entered.")


def decode_packet_type(raw_packet):
    packet_type = raw_packet >> 4
    switch = {
        0x02: "CONNACK",
        0x03: "PUBLISH",
        0x04: "PUBACK",
        0x05: "PUBREC",
        0x06: "PUBREL",
        0x07: "PUBCOMP",
        0x09: "SUBACK",
        0x0b: "UNSUBACK",
        0x0d: "PINGRESP",
        0x0e: "DISCONNECT",
        0x0f: "AUTH"
    }

    return switch[packet_type]


def determine_payload(topic):
    ret_val = ""
    if topic == "CPU":
        temp = CpuInformation()
        ret_val = temp.get_info()
    elif topic == "CPU Loads":
        temp = CpuUsage()
        ret_val = temp.get_info()
    elif topic == "CPU Temps":
        temp = CpuTemperatures()
        ret_val = temp.get_info()
    elif topic == "Memory":
        temp = MemoryInformation()
        ret_val = temp.get_info()
    elif topic == "Disk":
        temp = DiskInformation()
        ret_val = temp.get_info()
    elif topic == "Network":
        temp = NetworkInformation()
        ret_val = temp.get_info()

    return ret_val


class MQTTClient:
    def __init__(self, IP, port, client_username, client_password, client_name, keep_alive):
        # create a IPv4, TCP socket
        self.IP = IP
        self.port = port
        self.client_name = client_name
        self.keep_alive = keep_alive
        self.MQTT_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.last_received_packet = ""
        self.running = True
        self.sending_thread = Thread(target=self.run)
        self.receiving_thread = Thread(target=self.receive)
        self.keep_alive_thread = Thread(target=self.client_keep_alive)
        self.connect_packet = ConnectPacket(self.keep_alive, self.client_name,
                                            user_name=client_username, password=client_password)
        self.connect()
        self.send(self.connect_packet.pack())

    def connect(self):
        self.MQTT_socket.connect((self.IP, self.port))

    def send(self, data):
        print(datetime.now().strftime("%H:%M:%S") + "SENT " + str(data))
        try:
            self.MQTT_socket.sendall(data)
        except BrokenPipeError:
            logging.error("Broker suspended connection. Please restart application and use valid credentials.")

    def receive(self):
        try:
            while self.running is True:
                received_data = self.MQTT_socket.recv(4096)
                if received_data:
                    self.last_received_packet = decode_packet_type(received_data[0])
                    logging.info("\n<<" + self.client_name + ">>")
                    logging.info(datetime.now().strftime("%H:%M:%S") + ": RECEIVED " + decode_packet_type(
                        received_data[0]) + " PACKET.")
                    # if server sends us disconnect, we stop the threads
                    logging.info(datetime.now().strftime("%H:%M:%S") + ": RAW DATA: " + str(received_data))
        except ConnectionAbortedError:
            logging.error("Broker suspended connection. Please restart application and use valid credentials.")
        except ConnectionResetError:
            logging.error("Broker restarted connection. Please restart application and use valid credentials.")
        # for linux
        except BrokenPipeError:
            logging.error("Broker suspended connection. Please restart application and use valid credentials.")

    def disconnect(self):
        logging.error("DISCONNECTED.")
        # send disconnect package
        self.sending_thread.join()
        self.keep_alive_thread.join()
        self.running = False

    def run(self):
        pass

    # keep alive functionality
    def client_keep_alive(self):
        while self.running:
            sleep(int(self.keep_alive * 1.4))
            self.send(PingreqPacket().pack())


class MQTTPublisher(MQTTClient):
    def __init__(self, IP, port, client_username, client_password, client_name, topic,
                 keep_alive, qos, tip, interval):
        global g_generated_client_id
        super().__init__(IP, port, client_username, client_password, client_name, keep_alive)
        self.qos = qos
        self.tip = tip
        self.interval = interval
        self.generated_client_id = randint(1, 1 << 16 - 1)
        self.topic = topic
        self.publish_packet = None
        g_generated_client_id = self.generated_client_id
        # to be replaced in the future
        try:
            self.sending_thread.start()
            self.receiving_thread.start()
            # self.keep_alive_thread.start()
        except:
            logging.error("Failure when starting threads in " + str(type(self)) + ".")

    def run(self):
        global g_manual_publish_flag
        if self.tip == 2:
            if self.qos == 1 or self.qos == 0:
                while self.running:
                    temporary_payload = determine_payload(self.topic)
                    self.publish_packet = PublishPacket(self.topic, temporary_payload,
                                                        self.generated_client_id, self.qos)
                    self.send(self.publish_packet.pack())
                    sleep(self.interval)
            if self.qos == 2:
                while self.running:
                    temporary_payload = determine_payload(self.topic)
                    self.publish_packet = PublishPacket(self.topic, temporary_payload, self.generated_client_id,
                                                        self.qos)
                    if self.last_received_packet == "CONNACK" or self.last_received_packet == "PUBCOMP":
                        self.send(self.publish_packet.pack())
                    if self.last_received_packet == "PUBREC":
                        self.send(PubrelPacket(self.generated_client_id).pack())
                    sleep(self.interval)
        else:
            if self.qos == 1 or self.qos == 0:
                while self.running:
                    while g_manual_publish_flag != 0:
                        temporary_payload = determine_payload(self.topic)
                        self.publish_packet = PublishPacket(self.topic, temporary_payload, self.generated_client_id,
                                                            self.qos)
                        self.send(self.publish_packet.pack())
                        g_manual_publish_flag -= 1
            if self.qos == 2:
                while self.running:
                    while g_manual_publish_flag != 0:
                        temporary_payload = determine_payload(self.topic)
                        self.publish_packet = PublishPacket(self.topic, temporary_payload, self.generated_client_id,
                                                            self.qos)
                        if self.last_received_packet == "CONNACK" or self.last_received_packet == "PUBCOMP":
                            self.send(self.publish_packet.pack())
                            sleep(1)
                        if self.last_received_packet == "PUBREC":
                            self.send(PubrelPacket(self.generated_client_id).pack())
                            sleep(1)
                        g_manual_publish_flag -= 1


class MQTTSubscriber(MQTTClient):
    def __init__(self, IP, port, client_username, client_password, client_name, topics, keep_alive, qos_level):
        global g_generated_client_id
        super().__init__(IP, port, client_username, client_password, client_name, keep_alive)
        QoS = []
        self.qos_level = qos_level
        g_generated_client_id = randint(1, 1 << 16 - 1)

        # to be modified
        for topic in topics:
            QoS.append(qos_level)

        # must introduce a way to monitor how many clients are active
        # in order to give the client a pertinent ID.
        # env variable??
        self.subscribe_packet = SubscribePacket(topics, QoS, randint(1, 1 << 16 - 1))
        self.send(self.subscribe_packet.pack())
        try:
            self.sending_thread.start()
            self.receiving_thread.start()
            # self.keep_alive_thread.start()
        except:
            logging.error("Failure when starting threads in " + str(type(self)) + ".")

    def run(self):
        global g_generated_client_id
        if self.qos_level == 1 or self.qos_level == 0:
            while self.running:
                if self.last_received_packet == "PUBLISH":
                    self.send(PubackPacket(g_generated_client_id).pack())
                    self.last_received_packet = ""
        elif self.qos_level == 2:
            while self.running:
                if self.last_received_packet == "PUBLISH":
                    self.send(PubrecPacket(g_generated_client_id).pack())
                    self.last_received_packet = ""
                elif self.last_received_packet == "PUBREL":
                    self.send(PubcompPacket(g_generated_client_id).pack())
                    self.last_received_packet = ""


if __name__ == "__main__":
    gui = Gui()
    gui.root.mainloop()  # runs the gui in loop

# cb's -> PyDispatcher
# test wildcards ( $, +)
