import parse_protocol


if __name__ == '__main__':
    print('')
    parse_protocol.UnpackStream(b'\x04\x0e\x04\x01\x0c\x20\x00').dump()
    print('')
    parse_protocol.UnpackStream(b'\x02\x40\x20\x0b\x00\x11\x00\x06\x00\x0E\x03\x00\x01\x10\x02\x03\x02\x04\x03').dump()
