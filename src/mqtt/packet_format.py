class FixedHeader:

    def __init__(self,packet_type = None,flag = None,remaining_length = None):
        self.packet_type = packet_type
        self.flag = flag 
        self.remaining_length = remaining_length

    def set_packet_type(self, packet_type):
        if packet_type>=0 and packet_type<=15:
            self.packet_type = packet_type
        else:
            raise Exception("Invalid packet type: " + packet_type)

    def set_flags(self, flag):
        if flag>=0 and flag<=15:
            self.flag = flag
        else:
            raise Exception("Invalid flag " + flag)

    def set_remaining_length(self, remaining_length):
        self.remaining_length = remaining_length

    def get_packet_type(self):
        return self.packet_type
    
    def get_flag(self):
        return self.flag
    
    def get_remaining_length(self):
        return self.remaining_length


# Some types of MQTT Control Packet contain a Variable Header component. It resides between the Fixed Header and the Payload.
# The content of the Variable Header varies depending on the packet type. The Packet Identifier field of Variable Header is common in several packet types. 
# Variable header is separated in FIELDS.
class VariableHeader:
    def __init__(self):
        self.fields = {} # empty dictionary to stock all fields

    def add_field(self, field_name):
        self.fields[field_name] = None

    def set_field_value(self, field_name, value):
        if field_name not in self.fields:
            raise Exception("Unkown field to set. ("+field_name+")\n")
        else:
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.fields:
            raise Exception("Unkown field to get. ("+field_name+")\n")
        else:
            return self.fields[field_name]

    def get_header(self):
        return self.fields

# Some MQTT Control Packets contain a Payload as the final
# part of the packet. In the PUBLISH packet this is the Application Message 

class Payload:
    def __init__(self):
        self.fields = {}

    def add_field(self, field_name):
        self.fields[field_name] = None

    def set_field_value(self, field_name, value):
        if field_name not in self.fields:
            raise Exception("Unkown field to set. ("+field_name+")\n")
        else:
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.fields:
            raise Exception("Unkown field to get. ("+field_name+")\n")
        else:
            return self.fields[field_name]

    def get_payload(self):
        return self.fields

class ControlPacket:
    def __init__(self,fixed_header,variable_header = None,payload = None):
        self.fixed_header = fixed_header
        self.variable_header = variable_header
        self.payload = payload
    
    def get_fixed_header(self):
        return self.fixed_header

    def get_variable_header(self):
        return self.variable_header

    def get_payload(self):
        return self.payload


#testing purpose as of right now
if __name__ == "__main__":
    #testing all constructors
    packet = ControlPacket(FixedHeader(1,1,1),VariableHeader(),Payload())
    packet_2 = ControlPacket(FixedHeader(1,1,1),VariableHeader())
    packet_3 = ControlPacket(FixedHeader(1,1,1))

    print(packet.fixed_header.get_packet_type())
    print(packet_2.fixed_header.get_packet_type())
    print(packet_3.fixed_header.get_packet_type())
