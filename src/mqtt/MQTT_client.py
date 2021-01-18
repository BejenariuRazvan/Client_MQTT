import socket
from threading import Thread
from time import sleep
from control_packets import *
# from decode import decode_int
from datetime import datetime
from random import randint

IP_ = '127.0.0.1'
PORT = 1883
SIGNAL = 'received_packet'
g_generated_client_id = 0


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
    def __init__(self, IP, port, client_name, keep_alive):
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
        self.connect_packet = ConnectPacket(self.keep_alive, self.client_name)
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
                self.last_received_packet = decode_packet_type(received_data[0])
                print("\n<<" + self.client_name + ">>")
                print(datetime.now().strftime("%H:%M:%S") + ": RECEIVED " + decode_packet_type(
                    received_data[0]) + " PACKET.")
                # if server sends us disconnect, we stop the threads
                if decode_packet_type(received_data[0]) == "DISCONNECT":
                    self.disconnect()
                print(datetime.now().strftime("%H:%M:%S") + ": RAW DATA: " + str(received_data))

    def disconnect(self):
        print("DISCONNECTED.")
        # send disconnect package
        self.send(DisconnectPacket().pack())
        self.receiving_thread.join()
        self.sending_thread.join()
        self.keep_alive_thread.join()
        self.running = False

    def run(self):
        pass

    # keep alive functionality
    def client_keep_alive(self):
        while self.running:
            sleep(int(self.keep_alive*1.4))
            self.send(PingreqPacket().pack())


class MQTTPublisher(MQTTClient):
    def __init__(self, IP, port, client_name,topic,payload, keep_alive, qos,tip,interval):
        global g_generated_client_id
        super().__init__(IP, port, client_name, keep_alive)
        self.qos = qos
        self.tip=tip
        self.interval=interval
        self.generated_client_id = randint(1, 1 << 16 - 1)
        g_generated_client_id = self.generated_client_id
        # to be replaced in the future
        self.publish_packet = PublishPacket(topic, payload, self.generated_client_id, self.qos)
        self.sending_thread.start()
        self.receiving_thread.start()
        # self.keep_alive_thread.start()

    def run(self):
        if(self.tip==2):  
            if self.qos == 1 or self.qos == 0:
                while self.running:
                        self.send(self.publish_packet.pack())
                        sleep(self.interval)
            if self.qos == 2:
                while self.running: 
                    if self.last_received_packet == "CONNACK" or self.last_received_packet == "PUBCOMP":
                        self.send(self.publish_packet.pack())
                    elif self.last_received_packet == "PUBREC":
                        self.send(PubrelPacket(self.generated_client_id).pack())
                        sleep(self.interval)


class MQTTSubscriber(MQTTClient):
    def __init__(self, IP, port, client_name, topics, keep_alive, qos_level):
        super().__init__(IP, port, client_name, keep_alive)
        QoS = []
        self.qos_level = qos_level

        # to be modified
        for topic in topics:
            QoS.append(qos_level)

        # must introduce a way to monitor how many clients are active
        # in order to give the client a pertinent ID.
        # env variable??
        self.subscribe_packet = SubscribePacket(topics, QoS, randint(1, 1 << 16 - 1))
        self.send(self.subscribe_packet.pack())
        self.sending_thread.start()
        self.receiving_thread.start()
        self.keep_alive_thread.start()

    def run(self):
        if self.qos_level == 1:
            while self.running:
                if self.last_received_packet == "PUBLISH":
                    self.send(PubackPacket(randint(1, 1 << 16 - 1)).pack())
                    self.last_received_packet = ""
        elif self.qos_level == 2:
            while self.running:
                if self.last_received_packet == "PUBLISH":
                    self.send(PubrecPacket(g_generated_client_id).pack())
                    self.last_received_packet = ""
                elif self.last_received_packet == "PUBREL":
                    self.send(PubcompPacket(g_generated_client_id).pack())
                    self.last_received_packet = ""


# right now the output is mixed on the terminal, will be resolved when we get to the GUI phase

# Exemple:

    #publisher = MQTTPublisher(IP_, PORT, "publisher", 5, 2)
    #subscriber = MQTTSubscriber(IP_, PORT, "subscriber", ["/OS"], 5, 2)

# cb's -> PyDispatcher
# test wildcards ( $, +)
