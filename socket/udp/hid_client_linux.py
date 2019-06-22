#!/usr/bin/env python
from socket import *
import struct


def decode(buf):
    return True


def run(s, keyboard_dev, mouse_dev):
    keyboard_file = open(keyboard_dev, "wb")
    mouse_file = open(mouse_dev, "wb")
    fmt = 'HHI' # 'llHHI' remove 'll
    DATA_LEN = 10
    # cnt = 0
    while True:
        data, server_addr = s.recvfrom(1024)
        # print(''.join('{:02X} '.format(x) for x in data), server_addr, cnt)
        # cnt += 1
        if not (len(data) == DATA_LEN and decode(data)):
            continue
        key_event = data[2:]
        t, c, v = struct.unpack(fmt, key_event)
        if t == 1 and c < 0x0100:
            file_handler = keyboard_file
        else:
            file_handler = mouse_file
        try:
            # format llHHI -> sec, usec, type(1 or 2), code(keys), value(up/down)
            file_handler.write(b'\x00' * 8 + key_event)
            file_handler.write(b'\x00' * 16)
            file_handler.flush()
        except:
            continue

if __name__ == '__main__':
    addr=('192.168.5.10',23333)
    s = socket(AF_INET, SOCK_DGRAM)
    s.sendto(b'login', addr)
    run(s, '/dev/input/event3', '/dev/input/event6')
