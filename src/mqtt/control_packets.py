from packet_format import FixedHeader, VariableHeader, Payload, ControlPacket
from encode import serialize_string, serialize_8bit_int, serialize_4bit_int

class ConnectPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        self.payload = Payload()
        ################
        # FIXED HEADER #
        ################

        # 1 for connect
        self.fixed_header.set_packet_type(1)
        # flags -> reserved ( 0 )
        self.fixed_header.set_flags(0)
        # remaining length cannot be determined as of right now
        # to be updated after the population of the variable header
        self.fixed_header.set_remaining_length(0)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("protocol_name")
        self.variable_header.add_field("protocol_level")
        self.variable_header.add_field("connect_flags")
        self.variable_header.add_field("keep_alive")

        protocol_name = ""
        protocol_level = ""
        connect_flags = ""
        keep_alive = ""

        protocol_name += serialize_8bit_int(0) 
        protocol_name += serialize_8bit_int(4) 
        protocol_name += serialize_string("MQTT")
        protocol_level += serialize_8bit_int(4)
        connect_flags += serialize_8bit_int(0)
        keep_alive += serialize_8bit_int(0)
        keep_alive += serialize_8bit_int(0)

        self.variable_header.set_field_value("protocol_name",protocol_name)
        self.variable_header.set_field_value("protocol_level",protocol_level)
        # to be modified after initial creation
        self.variable_header.set_field_value("connect_flags",connect_flags)
        self.variable_header.set_field_value("keep_alive",keep_alive)

        ###########
        # PAYLOAD #
        ###########

        self.payload.add_field("client_identifier")
        self.payload.add_field("will_topic")
        self.payload.add_field("will_message")
        self.payload.add_field("user_name")
        self.payload.add_field("password")
    
    # TO DO: add functions to modify variable header connect flags&keep alive and payload


class ConnackPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        # The CONNACK Packet has no payload.
        self.payload = None 
        
        ################
        # FIXED HEADER #
        ################

        # 2 for connack
        self.fixed_header.set_packet_type(2)
        # flags -> reserved ( 0 )
        self.fixed_header.set_flags(0)
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.set_remaining_length(2)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("connect_ackowledge_flags")
        self.variable_header.add_field("connect_return_code")

        connect_ackowledge_flags = ""
        connect_return_code = ""

        connect_ackowledge_flags += serialize_8bit_int(0)
        connect_return_code += serialize_8bit_int(0)

        self.variable_header.set_field_value("connect_ackowledge_flags",connect_ackowledge_flags)
        self.variable_header.set_field_value("connect_return_code",connect_return_code)

    # TO DO: add functions to modify variable header 

class PublishPacket:
    def __init__(self, DUP = 0, QoS_level = 0, RETAIN = 0):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        self.payload = Payload() 
        
        ################
        # FIXED HEADER #
        ################

        # 3 for publish
        self.fixed_header.set_packet_type(3)
        # flags -> [DUP][QOS][QOS][RETAIN]
        temp_string = ""
        if DUP == 0 or DUP == 1:
            temp_string += str(DUP)
        else:
            raise Exception("Invalid DUP(" + DUP +")")


        if QoS_level == 0:
            temp_string += "00"
        elif QoS_level == 1:
            temp_string += "01"
        elif QoS_level == 2:
            temp_string += "10"
        else:
            raise Exception("Invalid Qos Level(" + QoS_level +")")

        if RETAIN == 0 or RETAIN == 1:
            temp_string += str(RETAIN)
        else:
            raise Exception("Invalid RETAIN(" + RETAIN +")")

        self.fixed_header.set_flags(int(temp_string,2))

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("topic_name")
        self.variable_header.add_field("packet_identifier")

        topic_name = ""
        packet_identifier = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)

        self.variable_header.set_field_value("topic_name",topic_name)
        self.variable_header.set_field_value("packet_identifier",packet_identifier)

        ###########
        # PAYLOAD #
        ###########

        self.payload.add_field("application_message")

        application_message = ""

        self.payload.set_field_value("application_message",application_message)

    # TO DO: add functions to modify variable header and payload

class PubackPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        # The PUBACK Packet has no payload.
        self.payload = None 
        
        ################
        # FIXED HEADER #
        ################

        # 4 for puback
        self.fixed_header.set_packet_type(4)
        # flags -> reserved ( 0 )
        self.fixed_header.set_flags(0)
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.set_remaining_length(2)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        packet_identifier = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)

        self.variable_header.set_field_value("packet_identifier",packet_identifier)

class PubrecPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        # The PUBREC Packet has no payload.
        self.payload = None 
        
        ################
        # FIXED HEADER #
        ################

        # 5 for pubrec
        self.fixed_header.set_packet_type(5)
        # flags -> reserved ( 0 )
        self.fixed_header.set_flags(0)
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.set_remaining_length(2)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        packet_identifier = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)

        self.variable_header.set_field_value("packet_identifier",packet_identifier)

class PubrelPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        # The PUBREL Packet has no payload.
        self.payload = None 
        
        ################
        # FIXED HEADER #
        ################

        # 6 for pubrel
        self.fixed_header.set_packet_type(6)
        # flags -> 0010
        self.fixed_header.set_flags(2)
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.set_remaining_length(2)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        packet_identifier = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)

        self.variable_header.set_field_value("packet_identifier",packet_identifier)

class PubcompPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        # The PUBCOMP  Packet has no payload.
        self.payload = None 
        
        ################
        # FIXED HEADER #
        ################

        # 7 for pubcomp
        self.fixed_header.set_packet_type(7)
        # flags -> reserved ( 0 )
        self.fixed_header.set_flags(0)
        # only 2 bytes in Variable header, no bytes in payload
        self.fixed_header.set_remaining_length(2)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        packet_identifier = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)

        self.variable_header.set_field_value("packet_identifier",packet_identifier)

class SubscribePacket:
    def __init__(self):
        self.fixed_header=FixedHeader()
        self.variable_header=VariableHeader()
        self.payload=Payload()

        ################
        # FIXED HEADER #
        ################

        # 8 for SUBSCRIBE
        self.fixed_header.set_packet_type(8)
        # flags -> reserved(2)
        self.fixed_header.set_flags(2)
        # remaining_length will be determined later
        self.fixed_header.set_remaining_length(0)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        self.variable_header.add_field("property_length")
        
        packet_identifier = ""
        property_length = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(10)
        property_length += serialize_8bit_int(0)

        self.variable_header.set_field_value("packet_identifier",packet_identifier)
        self.variable_header.set_field_value("property_length",property_length)

        ###########
        # PAYLOAD #
        ###########

        # to be completed

class SubackPacket:
    def __init__(self):
        self.fixed_header=FixedHeader()
        self.variable_header=VariableHeader()
        self.payload=Payload()

        ################
        # FIXED HEADER #
        ################
        
        # 9 for Suback
        self.fixed_header.set_packet_type(9)
        # flags -> reserved(0)
        self.fixed_header.set_flags(0)
        self.fixed_header.set_remaining_length(0)
        
        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        self.variable_header.add_field("property_length")
        

        packet_identifier = ""
        property_length = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)
       
        self.variable_header.set_field_value("packet_identifier",packet_identifier)
        self.variable_header.set_field_value("property_length",property_length)


        ###########
        # PAYLOAD #
        ###########

        # to be completed
        reasons_codes={}

class UnsubscribePacket:
    def __init__(self):
        self.fixed_header=FixedHeader()
        self.variable_header=VariableHeader()
        self.payload=Payload()

        ################
        # FIXED HEADER #
        ################
        
        # 10 for unsubscribe
        self.fixed_header.set_packet_type(10)
        # flags -> reserved(2)
        self.fixed_header.set_flags(2)
        self.fixed_header.set_remaining_length(0)
        
        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        self.variable_header.add_field("property_length")
        

        packet_identifier = ""
        property_length = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)
       
        self.variable_header.set_field_value("packet_identifier",packet_identifier)
        self.variable_header.set_field_value("property_length",property_length)


        ###########
        # PAYLOAD #
        ###########

        # to be completed
        reasons_codes={}

class UnsubackPacket:
    def __init__(self):
        self.fixed_header=FixedHeader()
        self.variable_header=VariableHeader()
        self.payload=Payload()

        ################
        # FIXED HEADER #
        ################
        
        # 11 for unsuback
        self.fixed_header.set_packet_type(11)
        # flags -> reserved(0)
        self.fixed_header.set_flags(0)
        self.fixed_header.set_remaining_length(0)
        
        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("packet_identifier")
        self.variable_header.add_field("property_length")
        

        packet_identifier = ""
        property_length = ""

        packet_identifier += serialize_8bit_int(0)
        packet_identifier += serialize_8bit_int(0)
       
        self.variable_header.set_field_value("packet_identifier",packet_identifier)
        self.variable_header.set_field_value("property_length",property_length)


        ###########
        # PAYLOAD #
        ###########

        # to be completed
        reasons_codes={}

class PingreqPacket:
    def __init__(self):
        self.fixed_header=FixedHeader()
        # no variable_header
        self.variable_header=None
        # no payload
        self.payload=None

        ################
        # FIXED HEADER #
        ################
        
        # 12 for pingreq
        self.fixed_header.set_packet_type(12)
        # flags -> reserved(0)
        self.fixed_header.set_flags(0)
        self.fixed_header.set_remaining_length(0)
        
class PingrespPacket:
    def __init__(self):
        self.fixed_header=FixedHeader()
        # no variable_header
        self.variable_header=None
        # no payload
        self.payload=None

        ################
        # FIXED HEADER #
        ################
        
        # 13 for pingreq
        self.fixed_header.set_packet_type(13)
        # flags -> reserved(0)
        self.fixed_header.set_flags(0)
        self.fixed_header.set_remaining_length(0)     


class DisconnectPacket:
    def __init__(self):
        self.fixed_header = FixedHeader()
        self.variable_header = VariableHeader()
        # no payload
        self.payload = None
        ################
        # FIXED HEADER #
        ################

        # 14 for disconnect
        self.fixed_header.set_packet_type(14)
        # flags -> reserved ( 0 )
        self.fixed_header.set_flags(0)
        # remaining length cannot be determined as of right now
        # to be updated after the population of the variable header
        self.fixed_header.set_remaining_length(0)

        ###################
        # VARIABLE HEADER #
        ###################

        self.variable_header.add_field("disconnect_reasons_code")
        self.variable_header.add_field("property_length")

        disconnect_reasons_code = ""
        property_length = ""
        self.variable_header.set_field_value("disconnect_reasons_code",disconnect_reasons_code)
        self.variable_header.set_field_value("property_length",property_length)
      
    



if __name__ == "__main__":
    test_1 = ConnectPacket()
    test_2 = ConnackPacket()
    test_3 = PublishPacket(1,2,1)
    test_4 = PubackPacket()
    test_5 = PubrecPacket()
    test_6 = PubrelPacket()
    test_7  = PubcompPacket()

    test_8  = SubscribePacket()
    test_9  = SubackPacket()
    test_10  = UnsubscribePacket()
    test_11  = UnsubackPacket()


    print("CONNECT")
    print(test_1.variable_header.get_field("protocol_name"))
    print(test_1.variable_header.get_field("protocol_level"))
    print("CONNACK")
    print(test_2.fixed_header.get_packet_type())
    print(test_2.fixed_header.get_flag())
    print(test_2.variable_header.get_field("connect_ackowledge_flags"))
    print(test_2.variable_header.get_field("connect_return_code"))
    print("PUBLISH")
    print(test_3.fixed_header.get_packet_type())
    print(test_3.fixed_header.get_flag())
    print(test_3.variable_header.get_field("topic_name"))
    print(test_3.variable_header.get_field("packet_identifier"))
    print("PUBACK")
    print(test_4.fixed_header.get_packet_type())
    print(test_4.fixed_header.get_flag())
    print(test_4.variable_header.get_field("packet_identifier"))
    print("PUBREC")
    print(test_5.fixed_header.get_packet_type())
    print(test_5.fixed_header.get_flag())
    print(test_5.variable_header.get_field("packet_identifier"))
    print("PUBREL")
    print(test_6.fixed_header.get_packet_type())
    print(test_6.fixed_header.get_flag())
    print(test_6.variable_header.get_field("packet_identifier"))
    print("PUBCOMP")
    print(test_7.fixed_header.get_packet_type())
    print(test_7.fixed_header.get_flag())
    print(test_7.variable_header.get_field("packet_identifier"))

    print("SUBSCRIBE")
    print(test_8.fixed_header.get_packet_type())
    print(test_8.fixed_header.get_flag())
    print(test_8.variable_header.get_field("packet_identifier"))
    print("SUBACK")
    print(test_9.fixed_header.get_packet_type())
    print(test_9.fixed_header.get_flag())
    print(test_9.variable_header.get_field("packet_identifier"))
    print("UNSUBSCRIBE")
    print(test_10.fixed_header.get_packet_type())
    print(test_10.fixed_header.get_flag())
    print(test_10.variable_header.get_field("packet_identifier"))
    print("UNSUBACK")
    print(test_11.fixed_header.get_packet_type())
    print(test_11.fixed_header.get_flag())
    print(test_11.variable_header.get_field("packet_identifier"))
    







