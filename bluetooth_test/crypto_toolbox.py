from aes import *
from cmac import *


def hexstr2bytes(string):
    assert (isinstance(string, str))
    return bytes.fromhex(string)


def hexdump(hex_bytes, rev=False):
    if rev:
        print(''.join('{:02X} '.format(x) for x in brev(hex_bytes)))
    else:
        print(''.join('{:02X} '.format(x) for x in hex_bytes))


def bxor(b1, b2): # use xor for bytes
    return bytes([a ^ b for a, b in zip(b1, b2)])


def brev(b):
    return b''.join([bytes([x]) for x in b][::-1])


def btc_e(key, d):
    _aes = AES(key)
    _res = _aes.encrypt_block(d)
    return _res


def btc_s1(k, r1, r2):
    return btc_e(k, r1[8:] + r2[8:])


def _btc_c1(k, r, p1, p2):
    _res = btc_e(k, bxor(r, p1))
    _res = btc_e(k, bxor(_res, p2))
    return _res


def btc_c1(k, r, preq, pres, iat, rat, ia, ra):
    p1 = pres + preq + rat + iat
    _p2 = ia + ra
    p2 = b'\x00'*(16-len(_p2)) + _p2
    _res = btc_e(k, bxor(r, p1))
    _res = btc_e(k, bxor(_res, p2))
    return _res


def btc_f5(W, N1, N2, A1, A2):
    salt = bytes.fromhex('6C88 8391 AAF5 A538 6037 0BDB 5A60 83BE')
    key_id = bytes.fromhex('62746c65')
    length = bytes.fromhex('0100')
    T = aes_cmac(salt, W)
    msg = b'\x01' + key_id + N1 + N2 + A1 + A2 + length
    res = aes_cmac(T, msg)
    return res


def btc_confirm_value(tk, rand, req_cmd, rep_cmd, init_dev_addr_type, init_dev_addr, rsp_dev_addr_type, rsp_dev_addr):
    return btc_c1(tk, rand, req_cmd, rep_cmd, init_dev_addr_type, init_dev_addr, rsp_dev_addr_type, rsp_dev_addr)


def btc_dm(k, r):
    assert(len(r) == 8)
    assert(len(k) == 16)
    r = b'\x00'*8 + r
    r = btc_e(k, r)
    return r[-2:]


def btc_ah(k, r):
    assert(len(k) == 16)
    r = b'\x00'*(16-len(r)) + r
    r = btc_e(k, r)
    return r[-3:]


if __name__ == '__main__':
    hexdump(hexstr2bytes('01 23 45 67 89 AB CD EF'))
    k = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    r1 = bytes.fromhex('000f0e0d0c0b0a091122334455667788')
    r2 = bytes.fromhex('010203040506070899aabbccddeeff00')
    hexdump(btc_s1(k, r1, r2))  # 9a 1f e1 f0 e8 b0 f4 9b 5b 42 16 ae 79 6d a0 62

    hexdump(btc_confirm_value(
        b'\x00' * 16,  # tk
        brev(hexstr2bytes('1ec1dd0928a3f67973f6fa39acc5642f')),  # rand
        brev(hexstr2bytes('01 04 00 2D 10 0f 0f')),  # req_cmd
        brev(hexstr2bytes('02 03 00 01 10 02 03')),  # rsp_cmd
        b'\x01',  # iat
        b'\x01',  # rat
        brev(hexstr2bytes('8a ea b5 ed 9b 6c')),  # ia
        brev(hexstr2bytes('5f 74 de c0 ad de')),  # ra
    ))  # f1580f3dbac17e2114b4fecc6fe43c37

    hexdump(btc_ah(
        brev(hexstr2bytes('30 46 1F D4 F5 49 93 C4 2D 6C DA DE 29 99 EA 9D')),  # IRK
        brev(hexstr2bytes('31 BB 4C')),
    ))  # 9D 89 3C
