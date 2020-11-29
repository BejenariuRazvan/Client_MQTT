def serialize_string(message):
    temporary_byte = 0
    payload = str("")

    for byte in message:
        # [2:] because bin introduces '0b' as the first 2 bits of th converted string
        # example: 0b01010110 -> [2:] results in 01010110
        temporary_byte = bin(ord(byte))[2:]
        temporary_byte = '%08d' %int(temporary_byte)
        payload += temporary_byte

    return payload

def serialize_8bit_int(integer):
    if integer <0 or integer >=255:
        raise Exception("Cannot serialize integer " + integer + "on 8 bits.")
    else:
        return '%08d' %int(str(bin(integer)[2:]))

def serialize_4bit_int(integer):
    if integer <0 or integer >=16:
        raise Exception("Cannot serialize integer " + integer + "on 4 bits.")
    else:
        return '%04d' %int(str(bin(integer)[2:]))