from packet_format import FixedHeader
import struct
from encode import encode_string, encode_int

class ConnectPacket:
    class ConnectFlags: 
        username_flag = 1
        password_flag = 1
        will_retain = 0
        will_qos = 1
        will_flag = 0
        clean_start = 0
    

    def __init__(self, client_id = "", will_properties = 0, will_topic = 0, will_payload = 0, user_name = "", password = "", keep_alive = 0):
        self.fixed_header = FixedHeader()
        self.client_id = client_id
        self.will_properties = will_properties
        self.will_topic = will_topic
        self.will_payload = will_payload
        self.user_name = user_name
        self.password = password
        self.keep_alive = keep_alive

    def pack(self):
        packed_data = bytearray()
        ################
        # FIXED HEADER #
        ################

        # 1 for connect
        self.fixed_header.packet_type = 0x01
        # flags -> reserved ( 0 )
        self.fixed_header.flags = 0x00
        # remaining length cannot be determined as of right now
        # to be updated after the population of the variable header
        self.fixed_header.remaining_length = 0

        ###################
        # VARIABLE HEADER #
        ###################

        #protocol name
        packed_data.append(0x00) # Length MSB (0)
        packed_data.append(0x04) # Length LSB (4)

        for char in 'MQTT':
            packed_data.append(ord(char)) # byte 3->6

        #protocol_version
        packed_data.append(0x05)
        
        #connect flags
        flags = 0
        flags |= self.ConnectFlags.username_flag << 7
        flags |= self.ConnectFlags.password_flag << 6
        flags |= self.ConnectFlags.will_retain << 5
        flags |= self.ConnectFlags.will_qos << 3
        flags |= self.ConnectFlags.will_flag << 2
        flags |= self.ConnectFlags.clean_start << 1

        packed_data.append(flags)

        # keep alive
        # !H -> unsigned short with Big Endian
        packed_data.extend(struct.pack('!H', self.keep_alive))

        ############
        # PAYLOAD #
        ############

        # The ClientID MUST be a UTF-8 Encoded String
         
        packed_data.extend(encode_string(self.client_id))

        if self.ConnectFlags.will_flag == 1:
            packed_data.extend(encode_string(self.will_properties))
            packed_data.extend(encode_string(self.will_topic))
            packed_data.extend(encode_string(self.will_payload))
        
        if self.ConnectFlags.username_flag == 1:
            packed_data.extend(encode_string(self.user_name))
        if self.ConnectFlags.password_flag == 1:
            packed_data.extend(encode_string(self.password))

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())

        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header
    
    # TO DO: add decode function

class ConnackPacket:
    def __init__(self, connect_ackowledge_flags = 0, connect_reason_code = 0):
        self.fixed_header = FixedHeader()
        self.connect_ackowledge_flags = connect_ackowledge_flags
        self.connect_reason_code = connect_reason_code

    def pack(self):  
        packed_data = bytearray()

        ################
        # FIXED HEADER #
        ################

        # 2 for connack
        self.fixed_header.packet_type = 0x02
        # flags -> reserved ( 0 )
        self.fixed_header.flags = 0x00
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.remaining_length = 0x02 

        packed_data.extend(self.fixed_header.pack())

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.extend(encode_int(self.connect_ackowledge_flags))
        packed_data.extend(encode_int(self.connect_reason_code))

        # The CONNACK Packet has no payload.
        
        return packed_data

class PublishPacket:
    def __init__(self, topic = '', payload = '', 
            packet_id = 0, QoS = 0, dup = 0, retain = 0):
        self.fixed_header = FixedHeader()
        self.topic = topic
        self.payload = payload
        self.packet_id = packet_id
        self.QoS = QoS
        self.dup = dup
        self.retain = retain

    def pack(self):
        packed_data = bytearray()

        ################
        # FIXED HEADER #
        ################

        # 3 for publish
        self.fixed_header.packet_type = 0x03
        # flags -> [DUP][QOS][QOS][RETAIN]
        
        self.fixed_header.flags |= self.dup << 3
        self.fixed_header.flags |= self.QoS << 1
        self.fixed_header.flags |= self.retain

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.extend(encode_string(self.topic))
        if self.QoS > 0:
            packed_data.extend(struct.pack('!H', self.packet_id))

        ###########
        # PAYLOAD #
        ###########

        packed_data.extend(bytearray(self.payload, 'utf-8'))
        
        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header
    # TO DO: add functions to modify variable header and payload

class PubackPacket:
    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
        self.fixed_header = FixedHeader()
        self.packet_id = packet_id    
        self.reason_code = reason_code
        self.property_length = property_length

    def pack(self):      
        packed_data = bytearray()  
        ################
        # FIXED HEADER #
        ################

        # 4 for puback
        self.fixed_header.packet_type = 0x04
        # flags -> reserved ( 0 )
        self.fixed_header.flags = 0x00
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.remaining_length = 2

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.extend(struct.pack('!H', self.packet_id))
        # Byte 3 in the Variable Header is the PUBACK Reason Code
        # If the Remaining Length is 2, then the Publish Reason Code has the value 0x00 (Success).
        packed_data.append(self.reason_code)
        # If the Remaining Length is less than 4 there is no Property Length and the value of 0 is used.
        packed_data.extend(encode_int(self.property_length))

        # it seems that the documentation talks about:
        # - reason string         
        # - user property 
        # but informations about these fields are rather unclear.

        # The PUBACK Packet has no payload.
        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header

class PubrecPacket:
    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
        self.fixed_header = FixedHeader()
        self.packet_id = packet_id    
        self.reason_code = reason_code
        self.property_length = property_length

    def pack(self):
        packed_data = bytearray()  
        ################
        # FIXED HEADER #
        ################

        # 5 for pubrec
        self.fixed_header.packet_type = 0x05
        # flags -> reserved ( 0 )
        self.fixed_header.flags = 0x00
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.remaining_length = 2

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.extend(struct.pack('!H', self.packet_id))
        # Byte 3 in the Variable Header is the PUBREC Reason Code
        # If the Remaining Length is 2, then the Publish Reason Code has the value 0x00 (Success).
        packed_data.append(self.reason_code)
        # If the Remaining Length is less than 4 there is no Property Length and the value of 0 is used.
        packed_data.extend(encode_int(self.property_length))

        # it seems that the documentation talks about:
        # - reason string         
        # - user property 
        # but informations about these fields are rather unclear.

        # The PUBREC Packet has no payload.

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header

class PubrelPacket:
    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
        self.fixed_header = FixedHeader()
        self.packet_id = packet_id    
        self.reason_code = reason_code
        self.property_length = property_length

    def pack(self):
        packed_data = bytearray()  
        ################
        # FIXED HEADER #
        ################

        # 6 for pubrel
        self.fixed_header.packet_type = 0x06
        # flags -> reserved ( 2 )
        self.fixed_header.flags = 0x02
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.remaining_length = 2

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.extend(struct.pack('!H', self.packet_id))
        # Byte 3 in the Variable Header is the PUBREL Reason Code
        # If the Remaining Length is 2, then the Publish Reason Code has the value 0x00 (Success).
        packed_data.append(self.reason_code)
        # If the Remaining Length is less than 4 there is no Property Length and the value of 0 is used.
        packed_data.extend(encode_int(self.property_length))

        # The PUBREL packet has no Payload.

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header

class PubcompPacket:
    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
        self.fixed_header = FixedHeader()
        self.packet_id = packet_id    
        self.reason_code = reason_code
        self.property_length = property_length

    def pack(self):
        packed_data = bytearray()  
        ################
        # FIXED HEADER #
        ################

        # 7 for pubcomp
        self.fixed_header.packet_type = 0x07
        # flags -> reserved ( 0 )
        self.fixed_header.flags = 0x00
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.remaining_length = 2

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.extend(struct.pack('!H', self.packet_id))
        # Byte 3 in the Variable Header is the PUBCOMP Reason Code
        # If the Remaining Length is 2, then the Publish Reason Code has the value 0x00 (Success).
        packed_data.append(self.reason_code)
        # If the Remaining Length is less than 4 there is no Property Length and the value of 0 is used.
        packed_data.extend(encode_int(self.property_length))

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header

class SubscribePacket:
    def __init__(self,topic,QoS, packet_id = 0, property_length = 0, Retain_Handling=[], RAP=[], NL=[]):
        self.fixed_header=FixedHeader()
        self.packet_id = packet_id
        self.property_length = property_length
        self.Retain_Handling = Retain_Handling
        self.RAP = RAP
        self.NL = NL
        self.topic = topic
        self.QoS = QoS

    def pack(self):
        packed_data=bytearray()

        #################
        # FIXED HEADER #
        ################
        # 8 for SUBSCRIBE
        self.fixed_header.packet_type=0x08
        # flags -> reserved(2)
        self.fixed_header.flags=0x02
        # remaining_length will be determined later
        self.fixed_header.remaining_length=0

        ###################
        # VARIABLE HEADER #
        ###################
        packed_data.extend(struct.pack('!H', self.packet_id))

        ###########
        # PAYLOAD #
        ###########
        i = 0

        # for every element in the topic list, get the message and the QoS 
        for elem in self.topic:
            packed_data.extend(encode_string(elem))
            aux = 0
            aux =aux << 7
            if len(self.Retain_Handling) != 0:
                aux |=self.Retain_Handling[i] <<5
            if len(self.RAP) != 0:
                aux |=self.RAP[i] <<3
            if len(self.NL) != 0:
                aux |=self.NL[i] <<2
            aux |=self.QoS[i]
            packed_data.extend(encode_int(aux))
            i+=1
        
        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header

        # to be completed

class SubackPacket:  
    def __init__(self,packet_id=0,reasons_code=[]):
        self.fixed_header = FixedHeader()
        self.packet_id = packet_id
        self.reasons_code = reasons_code
    
    def pack(self):
        packed_data=bytearray()
        ################
        # FIXED HEADER #
        ################

        # 9 for Suback
        self.fixed_header.packet_type=0x09
        # flags -> reserved(0)
        self.fixed_header.flags=0x00
        # remaining_length will be determined later
        self.fixed_header.remaining_length=0
        
        ###################
        # VARIABLE HEADER #
        ###################
        packed_data.extend(struct.pack('!H', self.packet_id))
        
        ###########
        # PAYLOAD #
        ###########
        for code in (self.reasons_code):
            packed_data.append(code)

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header
        # to be completed

class UnsubscribePacket:
    def __init__(self,packet_id=0,topic=[]):
        self.fixed_header = FixedHeader()
        self.packet_id=packet_id
        self.topic = topic

    def pack(self):
        packed_data=bytearray()        
        
        ################
        # FIXED HEADER #
        ################
        
        # 10 for unsubscribe
        self.fixed_header.packet_type=0x0a
        # flags -> reserved(2)
        self.fixed_header.flags=0x02
        self.fixed_header.remaining_length=0
        
        ###################
        # VARIABLE HEADER #
        ###################
        packed_data.extend(struct.pack('!H', self.packet_id))
        ###########
        # PAYLOAD #
        ###########
        for top in (self.topic):
            packed_data.extend(encode_string(top))

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header
        # to be completed

class UnsubackPacket:
    def __init__(self,packet_id=0):
        self.fixed_header = FixedHeader()
        self.packet_id=packet_id

    def pack(self):
        packed_data=bytearray()

        ################
        # FIXED HEADER #
        ################

        # 11 for unsuback
        self.fixed_header.packet_type=0xb
        # flags -> reserved(0)
        self.fixed_header.flags=0x00
        self.fixed_header.remaining_length=0
        
        ###################
        # VARIABLE HEADER #
        ###################
        packed_data.extend(struct.pack('!H', self.packet_id))

        ###########
        # PAYLOAD #
        ###########
        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header
        # to be completed

class PingreqPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()

    def pack(self): 
        packed_data=bytearray()       

        ################
        # FIXED HEADER #
        ################
        
        # 12 for pingreq
        self.fixed_header.packet_type=0x0c
        # flags -> reserved(0)
        self.fixed_header.flags=0x00
        self.fixed_header.remaining_length=0
        packed_data.extend(self.fixed_header.pack())

        # The PINGRESP packet has no Variable Header and no Payload.

        return packed_data

class PingrespPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
    def pack(self):
        packed_data=bytearray()

        ################
        # FIXED HEADER #
        ################
        
        # 13 for pingreq
        self.fixed_header.packet_type=0x0d
        # flags -> reserved(0)
        self.fixed_header.flags=0x00
        self.fixed_header.remaining_length=0     
        packed_data.extend(self.fixed_header.pack())

        # The PINGRESP packet has no Variable Header and no Payload.
        
        return packed_data


class DisconnectPacket:
    def __init__(self, reason_code = 0x00, property_length = 0, session_expiry_interval_id = 0, session_expiry_interval = 0):
        self.fixed_header = FixedHeader()
        self.reason_code = reason_code
        self.property_length = property_length
        self.session_expiry_interval_id = session_expiry_interval_id
        self.session_expiry_interval = session_expiry_interval 

    def pack(self):
        packed_data = bytearray()  
        ################
        # FIXED HEADER #
        ################

        # 14 for disconnect
        self.fixed_header.packet_type = 0x0E
        # flags -> reserved ( 0 )
        self.fixed_header.flags = 0x00
        self.fixed_header.remaining_length = 2

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.append(self.reason_code)
        packed_data.extend(encode_int(self.property_length))
        packed_data.extend(encode_int(self.session_expiry_interval_id))
        packed_data.extend(encode_int(self.session_expiry_interval))

        # The DISCONNECT packet has no Payload.

        # user properties ?
        # server reference ?

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header

class AuthPacket:

    def __init__(self, reason_code = 0x00, property_length = 0, auth_method_id = 0, auth_method = "", auth_data_id = 0, auth_data = "", reason_string_id = 0, reason_string = ""):
        self.fixed_header = FixedHeader()
        self.reason_code = reason_code
        self.property_length = property_length
        self.auth_method_id = auth_method_id
        self.auth_method = auth_method
        self.auth_data_id = auth_data_id
        self.auth_data = auth_data
        self.reason_string_id = reason_string_id
        self.reason_string = reason_string

    def pack(self):
        packed_data = bytearray()  
        ################
        # FIXED HEADER #
        ################

        # 15 for disconnect
        self.fixed_header.packet_type = 0x0F
        # flags -> reserved ( 0 )
        self.fixed_header.flags = 0x00
        self.fixed_header.remaining_length = 2

        ###################
        # VARIABLE HEADER #
        ###################

        packed_data.append(self.reason_code)
        packed_data.extend(encode_int(self.property_length))
        packed_data.extend(encode_int(self.auth_method_id))
        packed_data.extend(encode_string(self.auth_method))
        packed_data.extend(encode_int(self.auth_data_id))
        packed_data.extend(encode_string(self.auth_data))
        packed_data.extend(encode_int(self.reason_string_id))
        packed_data.extend(encode_string(self.reason_string))
        
        # The AUTH packet has no Payload.

        # user properties ?

        self.fixed_header.remaining_length = len(packed_data)
        packed_data_with_fixed_header = bytearray(self.fixed_header.pack())
        packed_data_with_fixed_header.extend(packed_data)

        return packed_data_with_fixed_header






