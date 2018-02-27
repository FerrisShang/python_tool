from aes import *


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
    return btc_e(k, r1 + r2)


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
    r1 = b'\x11\x22\x33\x44\x55\x66\x77\x88'
    r2 = b'\x99\xAA\xBB\xCC\xDD\xEE\xFF\x00'
    hexdump(btc_s1(k, r1, r2))  # 9a 1f e1 f0 e8 b0 f4 9b 5b 42 16 ae 79 6d a0 62

    hexdump(btc_confirm_value(
        b'\x00' * 16,  # tk
        brev(hexstr2bytes('31 EB 02 35 11 FE E5 81 43 26 C0 93 5C A8 EE 2D')),  # rand
        brev(hexstr2bytes('01 04 00 0D 10 03 03')),  # req_cmd
        brev(hexstr2bytes('02 03 00 01 10 02 03')),  # rsp_cmd
        b'\x01',  # iat
        b'\x00',  # rat
        brev(hexstr2bytes('F8 B4 F6 AF AC 7D')),  # ia
        brev(hexstr2bytes('01 A2 20 66 BF 01')),  # ra
    ))  # 0x7D015D1BAF109ACA14AC8592503838D6

    hexdump(btc_ah(
        brev(hexstr2bytes('30 46 1F D4 F5 49 93 C4 2D 6C DA DE 29 99 EA 9D')),  # IRK
        brev(hexstr2bytes('31 BB 4C')),
    ))  # 9D 89 3C
