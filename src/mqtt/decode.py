# function is described in MQTT 5  Documentation; section 1.5.5
def decode_int(data):
    # return decoded value and length consumed
    m = 1
    v = 0
    i = 0
    # We do not care about the length of data now
    # It will raise exception if the length is not enough
    while True:
        b = data[i]
        v += (b & 127) * m
        m *= 128
        i += 1
        if m > 128**3:
            raise Exception('Malformed Remaining Length')
        if b & 128 == 0:
            break
    return v, i
