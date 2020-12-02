import struct

# function is described in MQTT 5  Documentation; section 1.5.5
def encode_int(n):
    b = bytearray()
    v = 0
    while True:
        v = n & 127 # equals to n % 128, but should be faster
        n = n >> 7  # n / 2^7
        if n > 0:
            b.append(v | 128)
        else:
            b.append(v)
            break
    return b

def encode_string(s):
    b = bytearray()
    # Length (MSB)
    # Length (LSB)
    b.extend(struct.pack('!H', len(s)))
    # string
    b.extend(bytearray(s, 'utf-8'))

    return b
