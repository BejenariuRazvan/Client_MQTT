import socket
from threading import Thread
from time import sleep
from control_packets import *
# from decode import decode_int
from datetime import datetime

IP_ = '127.0.0.1'
PORT = 1883
SIGNAL = 'received_packet'


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


class MQTTClient:
    def __init__(self, IP, port, client_name):
        # create a IPv4, TCP socket
        self.IP = IP
        self.port = port
        self.client_name = client_name
        self.MQTT_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.sending_thread = Thread(target=self.run)
        self.receiving_thread = Thread(target=self.receive)
        self.connect_packet = ConnectPacket(60, self.client_name)
        self.connect()
        self.send(self.connect_packet.pack())

    def connect(self):
        self.MQTT_socket.connect((self.IP, self.port))

    def send(self, data):
        print(datetime.now().strftime("%H:%M:%S") + "SENT " + str(data))
        self.MQTT_socket.sendall(data)

    def receive(self):
        while self.running is True:
            received_data = self.MQTT_socket.recv(4096)
            if received_data:
                print("\n<<" + self.client_name + ">>")
                print(datetime.now().strftime("%H:%M:%S") + ": RECEIVED " + decode_packet_type(
                    received_data[0]) + " PACKET.")
                # if server sends us disconnect, we stop the threads
                if decode_packet_type(received_data[0]) == "DISCONNECT":
                    self.running = False
                print(datetime.now().strftime("%H:%M:%S") + ": RAW DATA: " + str(received_data))

    def disconnect(self):
        print("DISCONNECTED.")
        # send disconnect package
        self.send(DisconnectPacket().pack())
        self.receiving_thread.join()
        self.sending_thread.join()
        self.running = False

    def run(self):
        pass


class MQTTPublisher(MQTTClient):
    def __init__(self, IP, port, client_name):
        super().__init__(IP, port, client_name)
        self.publish_packet = PublishPacket("/OS", "CPU", 1, 1)
        self.sending_thread.start()
        self.receiving_thread.start()

    def run(self):
        while self.running:
            self.send(self.publish_packet.pack())
            sleep(2)


class MQTTSubscriber(MQTTClient):
    def __init__(self, IP, port, client_name, topics):
        super().__init__(IP, port, client_name)
        QoS = []

        # to be modified
        for topic in topics:
            QoS.append(1)

        # must introduce a way to monitor how many clients are active
        # in order to give the client a pertinent ID.
        # env variable??
        self.subscribe_packet = SubscribePacket(topics, QoS, 1)
        self.send(self.subscribe_packet.pack())
        self.sending_thread.start()
        self.receiving_thread.start()

    def run(self):
        while self.running:
            # must modify condition in the future
            sleep(1)


# right now the output is mixed on the terminal, will be resolved when we get to the GUI phase
publisher = MQTTPublisher(IP_, PORT, "publisher")
subscriber = MQTTSubscriber(IP_, PORT, "subscriber", ["/OS"])

# cb's -> PyDispatcher
# test wildcards ( $, +)
