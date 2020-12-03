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
