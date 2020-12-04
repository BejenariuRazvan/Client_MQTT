import socket,time
from control_packets import *

connect_package = ConnectPacket()
connack_package = ConnackPacket(1,1)
publish_package = PublishPacket()
puback_package = PubackPacket()
pubrec_package = PubrecPacket()
pubrel_package = PubrelPacket()
pubcomp_package = PubcompPacket()
subscribe_packet = SubscribePacket(["ana","are","mere"],[2,1,0],8,10,[0,0,0],[1,1,1],[1,0,0])
suback_packet = SubackPacket()
unsubscribe_packet = UnsubscribePacket()
unsuback_packet = UnsubackPacket()
pingreq_packet = PingreqPacket()
pingresp_packet = PingrespPacket()
disconnect_packet = DisconnectPacket()
auth_packet = AuthPacket()

packet_list = [ connect_package, connack_package, publish_package, puback_package, pubrec_package, pubrel_package, pubcomp_package, subscribe_packet, suback_packet, unsubscribe_packet, pingreq_packet, pingresp_packet, disconnect_packet, auth_packet ]

# Creaza un socket IPv4, TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Conectare la serverul care asculta la portul 5000
s.connect(('127.0.0.1',1883))
# Trimite date
for packet in packet_list:
    s.sendall(packet.pack())
    time.sleep(1)
# Asteapta date
data = s.recv(1024)
print('Am receptionat: ',data)
#Inchide conexiunea
s.close()