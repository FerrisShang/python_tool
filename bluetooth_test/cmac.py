from struct import unpack

__all__ = [
    'aes_cmac',
]

AES_128_ROUNDS = 10
AES_256_ROUNDS = 14

sbox = [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
        0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
        0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc,
        0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a,
        0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
        0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
        0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85,
        0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
        0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17,
        0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88,
        0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
        0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9,
        0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6,
        0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
        0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94,
        0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68,
        0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]


inv_sbox = [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38,
            0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
            0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87,
            0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
            0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d,
            0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
            0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2,
            0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
            0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16,
            0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
            0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda,
            0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
            0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a,
            0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
            0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02,
            0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
            0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea,
            0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
            0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85,
            0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
            0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89,
            0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
            0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20,
            0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
            0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31,
            0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
            0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d,
            0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
            0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0,
            0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
            0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26,
            0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]

def b2w(b0, b1, b2, b3):
    return (b0 << 24) + (b1 << 16) + (b2 << 8) + b3

def w2b(w):
    b0 = w >> 24
    b1 = w >> 16 & 0xff
    b2 = w >> 8 & 0xff
    b3 = w & 0xff

    return (b0, b1, b2, b3)

def gm2(b):
    return ((b << 1) ^ (0x1b & ((b >> 7) * 0xff))) & 0xff

def gm3(b):
    return gm2(b) ^ b

def gm4(b):
    return gm2(gm2(b))

def gm8(b):
    return gm2(gm4(b))

def gm09(b):
    return gm8(b) ^ b

def gm11(b):
    return gm8(b) ^ gm2(b) ^ b

def gm13(b):
    return gm8(b) ^ gm4(b) ^ b

def gm14(b):
    return gm8(b) ^ gm4(b) ^ gm2(b)

def substw(w):
    (b0, b1, b2, b3) = w2b(w)

    s0 = sbox[b0]
    s1 = sbox[b1]
    s2 = sbox[b2]
    s3 = sbox[b3]

    res = b2w(s0, s1, s2, s3)

    return res

def inv_substw(w):
    (b0, b1, b2, b3) = w2b(w)
    s0 = inv_sbox[b0]
    s1 = inv_sbox[b1]
    s2 = inv_sbox[b2]
    s3 = inv_sbox[b3]
    res = b2w(s0, s1, s2, s3)
    return res

def rolx(w, x):
    return ((w << x) | (w >> (32 - x))) & 0xffffffff

def next_128bit_key(prev_key, rcon):
    (w0, w1, w2, w3) = prev_key

    rol = rolx(w3, 8)
    subst = substw(rol)
    t = subst ^ (rcon << 24)
    k0 = w0 ^ t
    k1 = w1 ^ w0 ^ t
    k2 = w2 ^ w1 ^ w0 ^ t
    k3 = w3 ^ w2 ^ w1 ^ w0 ^ t
    return (k0, k1, k2, k3)

def key_gen128(key):
    round_keys = []
    round_keys.append(key)
    for i in range(10):
        round_keys.append(next_128bit_key(round_keys[i], get_rcon(i + 1)))
    return round_keys

def next_256it_key_a(key0, key1, rcon):
    (w0, w1, w2, w3) = key0
    (w4, w5, w6, w7) = key1
    sw = substw(rolx(w7, 8))
    rw = (rcon << 24)
    t = sw ^ rw
    k0 = w0 ^ t
    k1 = w1 ^ w0 ^ t
    k2 = w2 ^ w1 ^ w0 ^ t
    k3 = w3 ^ w2 ^ w1 ^ w0 ^ t
    return (k0, k1, k2, k3)

def next_256it_key_b(key0, key1):
    (w0, w1, w2, w3) = key0
    (w4, w5, w6, w7) = key1
    t = substw(w7)
    k0 = w0 ^ t
    k1 = w1 ^ w0 ^ t
    k2 = w2 ^ w1 ^ w0 ^ t
    k3 = w3 ^ w2 ^ w1 ^ w0 ^ t
    return (k0, k1, k2, k3)

def key_gen256(key):
    round_keys = []
    (k0, k1, k2, k3, k4, k5, k6, k7) = key
    round_keys.append((k0, k1, k2, k3))
    round_keys.append((k4, k5, k6, k7))
    j = 1
    for i in range(0, (AES_256_ROUNDS - 2), 2):
        k = next_256it_key_a(round_keys[i], round_keys[i + 1], get_rcon(j))
        round_keys.append(k)
        k = next_256it_key_b(round_keys[i + 1], round_keys[i + 2])
        round_keys.append(k)
        j += 1
    # One final key needs to be generated.
    k = next_256it_key_a(round_keys[12], round_keys[13], get_rcon(7))
    round_keys.append(k)
    return round_keys

def get_rcon(round):
    rcon = 0x8d
    for i in range(0, round):
        rcon = ((rcon << 1) ^ (0x11b & - (rcon >> 7))) & 0xff
    return rcon

def addroundkey(key, block):
    (w0, w1, w2, w3) = block
    (k0, k1, k2, k3) = key
    res_block = (w0 ^ k0, w1 ^ k1, w2 ^ k2, w3 ^ k3)
    return res_block

def mixw(w):
    (b0, b1, b2, b3) = w2b(w)
    mb0 = gm2(b0) ^ gm3(b1) ^ b2      ^ b3
    mb1 = b0      ^ gm2(b1) ^ gm3(b2) ^ b3
    mb2 = b0      ^ b1      ^ gm2(b2) ^ gm3(b3)
    mb3 = gm3(b0) ^ b1      ^ b2      ^ gm2(b3)
    return b2w(mb0, mb1, mb2, mb3)

def mixcolumns(block):
    (c0, c1, c2, c3) = block
    mc0 = mixw(c0)
    mc1 = mixw(c1)
    mc2 = mixw(c2)
    mc3 = mixw(c3)
    res_block = (mc0, mc1, mc2, mc3)
    return res_block

def subbytes(block):
    (w0, w1, w2, w3) = block
    res_block = (substw(w0), substw(w1), substw(w2), substw(w3))
    return res_block

def shiftrows(block):
    (w0, w1, w2, w3) = block
    c0 = w2b(w0)
    c1 = w2b(w1)
    c2 = w2b(w2)
    c3 = w2b(w3)
    ws0 = b2w(c0[0], c1[1],  c2[2],  c3[3])
    ws1 = b2w(c1[0], c2[1],  c3[2],  c0[3])
    ws2 = b2w(c2[0], c3[1],  c0[2],  c1[3])
    ws3 = b2w(c3[0], c0[1],  c1[2],  c2[3])
    res_block = (ws0, ws1, ws2, ws3)
    return res_block

def aes_encipher_block(key, block):
    tmp_block = block[:]
    # Get round keys based on the given key.
    if len(key) == 4:
        round_keys = key_gen128(key)
        num_rounds = AES_128_ROUNDS
    else:
        round_keys = key_gen256(key)
        num_rounds = AES_256_ROUNDS
    # Init round
    tmp_block4 = addroundkey(round_keys[0], block)
    # Main rounds
    for i in range(1 , (num_rounds)):
        tmp_block1 = subbytes(tmp_block4)
        tmp_block2 = shiftrows(tmp_block1)
        tmp_block3 = mixcolumns(tmp_block2)
        tmp_block4 = addroundkey(round_keys[i], tmp_block3)
    # Final round
    tmp_block1 = subbytes(tmp_block4)
    tmp_block2 = shiftrows(tmp_block1)
    tmp_block3 = addroundkey(round_keys[num_rounds], tmp_block2)
    return tmp_block3

def inv_mixw(w):
    (b0, b1, b2, b3) = w2b(w)
    mb0 = gm14(b0) ^ gm11(b1) ^ gm13(b2) ^ gm09(b3)
    mb1 = gm09(b0) ^ gm14(b1) ^ gm11(b2) ^ gm13(b3)
    mb2 = gm13(b0) ^ gm09(b1) ^ gm14(b2) ^ gm11(b3)
    mb3 = gm11(b0) ^ gm13(b1) ^ gm09(b2) ^ gm14(b3)
    return b2w(mb0, mb1, mb2, mb3)

def inv_mixcolumns(block):
    (c0, c1, c2, c3) = block
    mc0 = inv_mixw(c0)
    mc1 = inv_mixw(c1)
    mc2 = inv_mixw(c2)
    mc3 = inv_mixw(c3)
    res_block = (mc0, mc1, mc2, mc3)
    return res_block

def inv_shiftrows(block):
    (w0, w1, w2, w3) = block
    c0 = w2b(w0)
    c1 = w2b(w1)
    c2 = w2b(w2)
    c3 = w2b(w3)
    ws0 = b2w(c0[0], c3[1],  c2[2],  c1[3])
    ws1 = b2w(c1[0], c0[1],  c3[2],  c2[3])
    ws2 = b2w(c2[0], c1[1],  c0[2],  c3[3])
    ws3 = b2w(c3[0], c2[1],  c1[2],  c0[3])
    res_block = (ws0, ws1, ws2, ws3)
    return res_block

def inv_subbytes(block):
    (w0, w1, w2, w3) = block
    res_block = (inv_substw(w0), inv_substw(w1), inv_substw(w2), inv_substw(w3))
    return res_block

def aes_decipher_block(key, block):
    tmp_block = block[:]
    # Get round keys based on the given key.
    if len(key) == 4:
        round_keys = key_gen128(key)
        num_rounds = AES_128_ROUNDS
    else:
        round_keys = key_gen256(key)
        num_rounds = AES_256_ROUNDS
    # Initial round
    tmp_block1 = addroundkey(round_keys[len(round_keys) - 1], tmp_block)
    tmp_block2 = inv_shiftrows(tmp_block1)
    tmp_block4 = inv_subbytes(tmp_block2)
    # Main rounds
    for i in range(1, (num_rounds)):
        tmp_block1 = addroundkey(round_keys[(len(round_keys) - i - 1)], tmp_block4)
        tmp_block2 = inv_mixcolumns(tmp_block1)
        tmp_block3 = inv_shiftrows(tmp_block2)
        tmp_block4 = inv_subbytes(tmp_block3)
    # Final round
    res_block = addroundkey(round_keys[0], tmp_block4)
    return res_block

R128 = (0, 0, 0, 0x00000087)
MAX128 = ((2**128) - 1)
AES_BLOCK_LENGTH = 128

def xor_words(a, b):
    c = (a[0] ^ b[0], a[1] ^ b[1], a[2] ^ b[2], a[3] ^ b[3])
    return c

def shift_words(wl):
    w = ((wl[0] << 96) + (wl[1] << 64) + (wl[2] << 32) + wl[3]) & MAX128
    ws = w << 1 & MAX128
    return ((ws >> 96) & 0xffffffff, (ws >> 64) & 0xffffffff,
            (ws >> 32) & 0xffffffff, ws & 0xffffffff)

def pad_block(block, bitlen):
    bw = ((block[0] << 96) + (block[1] << 64) + (block[2] << 32) + block[3]) & MAX128
    bitstr = "1" * bitlen + "0" * (128 - bitlen)
    bitmask = int(bitstr, 2)
    masked = bw & bitmask
    padded = masked + (1 << (127 - bitlen))
    padded_block = ((padded >> 96) & 0xffffffff, (padded >> 64) & 0xffffffff,
                    (padded >> 32) & 0xffffffff, padded & 0xffffffff)
    return padded_block

def cmac_gen_subkeys(key):
    L = aes_encipher_block(key, (0, 0, 0, 0))

    Pre_K1 = shift_words(L)
    MSBL = (L[0] >> 31) & 0x01
    if MSBL:
        K1 = xor_words(Pre_K1, R128)
    else:
        K1 = Pre_K1

    Pre_K2 = shift_words(K1)
    MSBK1 = (K1[0] >> 31) & 0x01
    if MSBK1:
        K2 = xor_words(Pre_K2, R128)
    else:
        K2 = Pre_K2
    return K1, K2

def cmac(key, message, final_length):
    (K1, K2) = cmac_gen_subkeys(key)
    state = (0x00000000, 0x00000000, 0x00000000, 0x00000000)
    blocks = len(message)
    if blocks == 0:
        # Empty message.
        paddded_block = pad_block(state, 0)
        tweak = xor_words(paddded_block, K2)
        M = aes_encipher_block(key, tweak)
    else:
        for i in range(blocks - 1):
            state = xor_words(state, message[i])
            state = aes_encipher_block(key, state)
        if final_length == AES_BLOCK_LENGTH:
            tweak = xor_words(K1, message[(blocks - 1)])
        else:
            padded_block = pad_block(message[(blocks - 1)], final_length)
            tweak = xor_words(K2, padded_block)
        state = xor_words(state, tweak)
        M = aes_encipher_block(key, state)
    return M

def aes_cmac(key, message):
    assert(len(key) == 16)
    key = unpack('>IIII', key)
    if len(message) == 0:
        final_len = 0
        data = []
    else:
        final_len = 128 if (len(message) % 16) == 0 else (len(message) % 16) * 8
        if len(message) % 16 > 0:
            message += b'\x00' * (16 - (len(message) % 4))
        msg = [int.from_bytes(message[n*4:n*4+4], 'big') for n in range(len(message)//4)]
        data = [tuple(msg[n*4:n*4+4]) for n in range(len(msg)//4)]
    _ = cmac(key, data, final_len)
    return b''.join([b.to_bytes(4, 'big') for b in _])
