from encode import *

class FixedHeader:

    packet_type = 0x00
    flags = 0x00
    remaining_length = 0

    def pack(self):
        hdr = bytearray()
        v = self.packet_type << 4 # first four bits
        v |= self.flags & 0x0F # last four bits
        hdr.append(v)
        hdr.extend(encode_int(self.remaining_length))
        return hdr

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
