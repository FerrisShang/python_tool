# -*- coding: utf-8 -*-
from struct import unpack

__all__ = [
    'PinYin'
]


class PinYin:
    path = 'pin.dat'
    pin_list = None
    pin_dict = {}

    @staticmethod
    def get(ch):
        if PinYin.pin_list is None:
            fm = open(PinYin.path, 'rb')
            PinYin.pin_list = bytes([int(x) ^ 0x5F for x in fm.read(2048)]).decode('utf-8').strip().split()
            PinYin.pin_dict = {}
            while True:
                dat = fm.read(4)
                if dat == b'':
                    break
                dat = unpack('<I', dat)[0]
                k, p, s = ((dat >> 12) & 0xFFFFF, (dat >> 2) & 0x3FF, dat & 0x03)
                PinYin.pin_dict[k] = [PinYin.pin_list[p].lower(), s]
            fm.close()
        if ord(ch) in PinYin.pin_dict:
            return PinYin.pin_dict[ord(ch)]
        else:
            return (ch, 0)

if __name__ == '__main__':
    for c in '你好!':
        print(PinYin.get(c))
