import socket,time
import threading
import time
from control_packets import *

class MQTTClient():
    def __init__(self, IP, port):
        # create a IPv4, TCP socket
        self.IP = IP
        self.port = port
        self.MQTT_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def connect(self):
        self.MQTT_socket.connect((self.IP,self.port))

    def send(self,data):
        print("SENT " + str(data))
        self.MQTT_socket.sendall(data)
    
    def receive(self):
        received_data = self.MQTT_socket.recv(1024)
        print("RECEIVED: " + str(received_data))

        return received_data

    def disconnect(self):
        print("DISCONNECTED.")
        self.running = False

    def run(self):
        connect_packet = ConnectPacket(60, "client")
        self.connect()
        self.send(connect_packet.pack())
        while self.running == True:
            if len(self.receive()) == 0:
                break

client = MQTTClient('127.0.0.1',1883)
client.run()