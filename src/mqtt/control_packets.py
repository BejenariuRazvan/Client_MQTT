from packet_format import FixedHeader, ControlPacket
import struct
from encode import encode_string, encode_int

class ConnectPacket:
    fixed_header = FixedHeader()
    class ConnectFlags: 
        username_flag = 1
        password_flag = 1
        will_retain = 0
        will_qos = 1
        will_flag = 0
        clean_start = 0
    
    keep_alive = 0
    client_id = ""
    will_properties = ""
    will_topic = ""
    will_payload = ""
    user_name = ""
    password = ""

    def __init__(self, client_id, will_properties, will_topic, will_payload, user_name, password, keep_alive):
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
    fixed_header = FixedHeader()

    def __init__(self, connect_ackowledge_flags = 0, connect_reason_code = 0):
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
    fixed_header = FixedHeader()

    dup = 0
    QoS = 0
    retain = 0
    topic = ""
    packet_id = 0
    
    def __init__(self, topic = '', payload = '', 
            packet_id = 0, QoS = 0, dup = 0, retain = 0):
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
    fixed_header = FixedHeader()

    packet_id = 0

    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
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

        packed_data.extend(self.fixed_header.pack())

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


        return packed_data

class PubrecPacket:
    fixed_header = FixedHeader()

    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
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

class PubrelPacket:
    fixed_header = FixedHeader()

    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
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

 
class PubcompPacket:
    fixed_header = FixedHeader()

    def __init__(self, packet_id = 0, reason_code = 0x00, property_length = 0):
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

# class SubscribePacket:
#     def __init__(self):
#         self.fixed_header=FixedHeader()
#         self.variable_header=VariableHeader()
#         self.payload=Payload()

#         ################
#         # FIXED HEADER #
#         ################

#         # 8 for SUBSCRIBE
#         self.fixed_header.set_packet_type(8)
#         # flags -> reserved(2)
#         self.fixed_header.set_flags(2)
#         # remaining_length will be determined later
#         self.fixed_header.set_remaining_length(0)

#         ###################
#         # VARIABLE HEADER #
#         ###################

#         self.variable_header.add_field("packet_identifier")
#         self.variable_header.add_field("property_length")
        
#         packet_identifier = ""
#         property_length = ""

#         packet_identifier += serialize_8bit_int(0)
#         packet_identifier += serialize_8bit_int(10)
#         property_length += serialize_8bit_int(0)

#         self.variable_header.set_field_value("packet_identifier",packet_identifier)
#         self.variable_header.set_field_value("property_length",property_length)

#         ###########
#         # PAYLOAD #
#         ###########

#         # to be completed

# class SubackPacket:
#     def __init__(self):
#         self.fixed_header=FixedHeader()
#         self.variable_header=VariableHeader()
#         self.payload=Payload()

#         ################
#         # FIXED HEADER #
#         ################
        
#         # 9 for Suback
#         self.fixed_header.set_packet_type(9)
#         # flags -> reserved(0)
#         self.fixed_header.set_flags(0)
#         self.fixed_header.set_remaining_length(0)
        
#         ###################
#         # VARIABLE HEADER #
#         ###################

#         self.variable_header.add_field("packet_identifier")
#         self.variable_header.add_field("property_length")
        

#         packet_identifier = ""
#         property_length = ""

#         packet_identifier += serialize_8bit_int(0)
#         packet_identifier += serialize_8bit_int(0)
       
#         self.variable_header.set_field_value("packet_identifier",packet_identifier)
#         self.variable_header.set_field_value("property_length",property_length)


#         ###########
#         # PAYLOAD #
#         ###########

#         # to be completed
#         reasons_codes={}

# class UnsubscribePacket:
#     def __init__(self):
#         self.fixed_header=FixedHeader()
#         self.variable_header=VariableHeader()
#         self.payload=Payload()

#         ################
#         # FIXED HEADER #
#         ################
        
#         # 10 for unsubscribe
#         self.fixed_header.set_packet_type(10)
#         # flags -> reserved(2)
#         self.fixed_header.set_flags(2)
#         self.fixed_header.set_remaining_length(0)
        
#         ###################
#         # VARIABLE HEADER #
#         ###################

#         self.variable_header.add_field("packet_identifier")
#         self.variable_header.add_field("property_length")
        

#         packet_identifier = ""
#         property_length = ""

#         packet_identifier += serialize_8bit_int(0)
#         packet_identifier += serialize_8bit_int(0)
       
#         self.variable_header.set_field_value("packet_identifier",packet_identifier)
#         self.variable_header.set_field_value("property_length",property_length)


#         ###########
#         # PAYLOAD #
#         ###########

#         # to be completed
#         reasons_codes={}

# class UnsubackPacket:
#     def __init__(self):
#         self.fixed_header=FixedHeader()
#         self.variable_header=VariableHeader()
#         self.payload=Payload()

#         ################
#         # FIXED HEADER #
#         ################
        
#         # 11 for unsuback
#         self.fixed_header.set_packet_type(11)
#         # flags -> reserved(0)
#         self.fixed_header.set_flags(0)
#         self.fixed_header.set_remaining_length(0)
        
#         ###################
#         # VARIABLE HEADER #
#         ###################

#         self.variable_header.add_field("packet_identifier")
#         self.variable_header.add_field("property_length")
        

#         packet_identifier = ""
#         property_length = ""

#         packet_identifier += serialize_8bit_int(0)
#         packet_identifier += serialize_8bit_int(0)
       
#         self.variable_header.set_field_value("packet_identifier",packet_identifier)
#         self.variable_header.set_field_value("property_length",property_length)


#         ###########
#         # PAYLOAD #
#         ###########

#         # to be completed
#         reasons_codes={}

# class PingreqPacket:
#     def __init__(self):
#         self.fixed_header=FixedHeader()
#         # no variable_header
#         self.variable_header=None
#         # no payload
#         self.payload=None

#         ################
#         # FIXED HEADER #
#         ################
        
#         # 12 for pingreq
#         self.fixed_header.set_packet_type(12)
#         # flags -> reserved(0)
#         self.fixed_header.set_flags(0)
#         self.fixed_header.set_remaining_length(0)
        
# class PingrespPacket:
#     def __init__(self):
#         self.fixed_header=FixedHeader()
#         # no variable_header
#         self.variable_header=None
#         # no payload
#         self.payload=None

#         ################
#         # FIXED HEADER #
#         ################
        
#         # 13 for pingreq
#         self.fixed_header.set_packet_type(13)
#         # flags -> reserved(0)
#         self.fixed_header.set_flags(0)
#         self.fixed_header.set_remaining_length(0)     


# class DisconnectPacket:
#     def __init__(self):
#         self.fixed_header = FixedHeader()
#         self.variable_header = VariableHeader()
#         # no payload
#         self.payload = None
#         ################
#         # FIXED HEADER #
#         ################

#         # 14 for disconnect
#         self.fixed_header.set_packet_type(14)
#         # flags -> reserved ( 0 )
#         self.fixed_header.set_flags(0)
#         # remaining length cannot be determined as of right now
#         # to be updated after the population of the variable header
#         self.fixed_header.set_remaining_length(0)

#         ###################
#         # VARIABLE HEADER #
#         ###################

#         self.variable_header.add_field("disconnect_reasons_code")
#         self.variable_header.add_field("property_length")

#         disconnect_reasons_code = ""
#         property_length = ""
#         self.variable_header.set_field_value("disconnect_reasons_code",disconnect_reasons_code)
#         self.variable_header.set_field_value("property_length",property_length)
      
    



# if __name__ == "__main__":
#     test_1 = ConnectPacket()
#     test_2 = ConnackPacket()
#     test_3 = PublishPacket(1,2,1)
#     test_4 = PubackPacket()
#     test_5 = PubrecPacket()
#     test_6 = PubrelPacket()
#     test_7  = PubcompPacket()

#     test_8  = SubscribePacket()
#     test_9  = SubackPacket()
#     test_10  = UnsubscribePacket()
#     test_11  = UnsubackPacket()


#     print("CONNECT")
#     print(test_1.variable_header.get_field("protocol_name"))
#     print(test_1.variable_header.get_field("protocol_level"))
#     print("CONNACK")
#     print(test_2.fixed_header.get_packet_type())
#     print(test_2.fixed_header.get_flag())
#     print(test_2.variable_header.get_field("connect_ackowledge_flags"))
#     print(test_2.variable_header.get_field("connect_return_code"))
#     print("PUBLISH")
#     print(test_3.fixed_header.get_packet_type())
#     print(test_3.fixed_header.get_flag())
#     print(test_3.variable_header.get_field("topic_name"))
#     print(test_3.variable_header.get_field("packet_identifier"))
#     print("PUBACK")
#     print(test_4.fixed_header.get_packet_type())
#     print(test_4.fixed_header.get_flag())
#     print(test_4.variable_header.get_field("packet_identifier"))
#     print("PUBREC")
#     print(test_5.fixed_header.get_packet_type())
#     print(test_5.fixed_header.get_flag())
#     print(test_5.variable_header.get_field("packet_identifier"))
#     print("PUBREL")
#     print(test_6.fixed_header.get_packet_type())
#     print(test_6.fixed_header.get_flag())
#     print(test_6.variable_header.get_field("packet_identifier"))
#     print("PUBCOMP")
#     print(test_7.fixed_header.get_packet_type())
#     print(test_7.fixed_header.get_flag())
#     print(test_7.variable_header.get_field("packet_identifier"))

#     print("SUBSCRIBE")
#     print(test_8.fixed_header.get_packet_type())
#     print(test_8.fixed_header.get_flag())
#     print(test_8.variable_header.get_field("packet_identifier"))
#     print("SUBACK")
#     print(test_9.fixed_header.get_packet_type())
#     print(test_9.fixed_header.get_flag())
#     print(test_9.variable_header.get_field("packet_identifier"))
#     print("UNSUBSCRIBE")
#     print(test_10.fixed_header.get_packet_type())
#     print(test_10.fixed_header.get_flag())
#     print(test_10.variable_header.get_field("packet_identifier"))
#     print("UNSUBACK")
#     print(test_11.fixed_header.get_packet_type())
#     print(test_11.fixed_header.get_flag())
#     print(test_11.variable_header.get_field("packet_identifier"))
    







