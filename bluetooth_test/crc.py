import struct

__all__ = [
    'Crc',
]

class Crc:
    def __init__(self, poly, initCrc=~0, rev=True, xorOut=0, initialize=True):
        if not initialize:
            # Don't want to perform the initialization when using new or copy
            # to create a new instance.
            return

        (sizeBits, initCrc, xorOut) = _verifyParams(poly, initCrc, xorOut)
        self.digest_size = sizeBits//8
        self.initCrc = initCrc
        self.xorOut = xorOut

        self.poly = poly
        self.reverse = rev

        (crcfun, table) = _mkCrcFun(poly, sizeBits, initCrc, rev, xorOut)
        self._crc = crcfun
        self.table = table

        self.crcValue = self.initCrc

    def __str__(self):
        lst = []
        lst.append('poly = 0x%X' % self.poly)
        lst.append('reverse = %s' % self.reverse)
        fmt = '0x%%0%dX' % (self.digest_size*2)
        lst.append('initCrc  = %s' % (fmt % self.initCrc))
        lst.append('xorOut   = %s' % (fmt % self.xorOut))
        lst.append('crcValue = %s' % (fmt % self.crcValue))
        return '\n'.join(lst)

    def new(self, arg=None):
        '''Create a new instance of the Crc class initialized to the same
        values as the original instance.  The current CRC is set to the initial
        value.  If a string is provided in the optional arg parameter, it is
        passed to the update method.
        '''
        n = Crc(poly=None, initialize=False)
        n._crc = self._crc
        n.digest_size = self.digest_size
        n.initCrc = self.initCrc
        n.xorOut = self.xorOut
        n.table = self.table
        n.crcValue = self.initCrc
        n.reverse = self.reverse
        n.poly = self.poly
        if arg is not None:
            n.update(arg)
        return n

    def copy(self):
        '''Create a new instance of the Crc class initialized to the same
        values as the original instance.  The current CRC is set to the current
        value.  This allows multiple CRC calculations using a common initial
        string.
        '''
        c = self.new()
        c.crcValue = self.crcValue
        return c

    def update(self, data):
        '''Update the current CRC value using the string specified as the data
        parameter.
        '''
        self.crcValue = self._crc(data, self.crcValue)

    def digest(self):
        '''Return the current CRC value as a string of bytes.  The length of
        this string is specified in the digest_size attribute.
        '''
        n = self.digest_size
        crc = self.crcValue
        lst = []
        while n > 0:
            lst.append(crc & 0xFF)
            crc >>= 8
            n -= 1
        lst.reverse()
        return bytes(lst)

    def hexdigest(self):
        '''Return the current CRC value as a string of hex digits.  The length
        of this string is twice the digest_size attribute.
        '''
        n = self.digest_size
        crc = self.crcValue
        lst = []
        while n > 0:
            lst.append('%02X' % (crc & 0xFF))
            crc >>= 8
            n -= 1
        lst.reverse()
        return ''.join(lst)

    @staticmethod
    def ll_crc(initCrc, data, poly=0x100065B):
        initCrc = _bitrev(initCrc, _verifyPoly(poly))
        crc = Crc(poly, initCrc)
        crc.update(data)
        return crc.crcValue

#-----------------------------------------------------------------------------
def mkCrcFun(poly, initCrc=~0, rev=True, xorOut=0):
    '''Return a function that computes the CRC using the specified polynomial.

    poly -- integer representation of the generator polynomial
    initCrc -- default initial CRC value
    rev -- when true, indicates that the data is processed bit reversed.
    xorOut -- the final XOR value

    The returned function has the following user interface
    def crcfun(data, crc=initCrc):
    '''

    # First we must verify the params
    (sizeBits, initCrc, xorOut) = _verifyParams(poly, initCrc, xorOut)
    # Make the function (and table), return the function
    return _mkCrcFun(poly, sizeBits, initCrc, rev, xorOut)[0]

#-----------------------------------------------------------------------------
# Naming convention:
# All function names ending with r are bit reverse variants of the ones
# without the r.

#-----------------------------------------------------------------------------
# Check the polynomial to make sure that it is acceptable and return the number
# of bits in the CRC.

def _verifyPoly(poly):
    msg = 'The degree of the polynomial must be 8, 16, 24, 32 or 64'
    for n in (8,16,24,32,64):
        low = 1<<n
        high = low*2
        if low <= poly < high:
            return n
    raise ValueError(msg)

#-----------------------------------------------------------------------------
# Bit reverse the input value.

def _bitrev(x, n):
    y = 0
    for i in range(n):
        y = (y << 1) | (x & 1)
        x = x >> 1
    return y

#-----------------------------------------------------------------------------
# The following functions compute the CRC for a single byte.  These are used
# to build up the tables needed in the CRC algorithm.  Assumes the high order
# bit of the polynomial has been stripped off.

def _bytecrc(crc, poly, n):
    mask = 1<<(n-1)
    for i in range(8):
        if crc & mask:
            crc = (crc << 1) ^ poly
        else:
            crc <<= 1
    mask = (1<<n) - 1
    crc &= mask
    return crc

def _bytecrc_r(crc, poly, n):
    for i in range(8):
        if crc & 1:
            crc = (crc >> 1) ^ poly
        else:
            crc >>= 1
    mask = (1<<n) - 1
    crc &= mask
    return crc

#-----------------------------------------------------------------------------
# The following functions compute the table needed to compute the CRC.  The
# table is returned as a list.  Note that the array module does not support
# 64-bit integers on a 32-bit architecture as of Python 2.3.
#
# These routines assume that the polynomial and the number of bits in the CRC
# have been checked for validity by the caller.

def _mkTable(poly, n):
    mask = (1<<n) - 1
    poly = poly & mask
    table = [_bytecrc(i<<(n-8),poly,n) for i in range(256)]
    return table

def _mkTable_r(poly, n):
    mask = (1<<n) - 1
    poly = _bitrev(poly & mask, n)
    table = [_bytecrc_r(i,poly,n) for i in range(256)]
    return table

#-----------------------------------------------------------------------------
# Map the CRC size onto the functions that handle these sizes.

def _get_buffer_view(in_obj):
    if isinstance(in_obj, str):
        raise TypeError('Unicode-objects must be encoded before calculating a CRC')
    mv = memoryview(in_obj)
    if mv.ndim > 1:
        raise BufferError('Buffer must be single dimension')
    return mv

def _crc8(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFF
    for x in mv.tobytes():
        crc = table[x ^ crc]
    return crc

def _crc8r(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFF
    for x in mv.tobytes():
        crc = table[x ^ crc]
    return crc

def _crc16(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFF
    for x in mv.tobytes():
        crc = table[x ^ ((crc>>8) & 0xFF)] ^ ((crc << 8) & 0xFF00)
    return crc

def _crc16r(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFF
    for x in mv.tobytes():
        crc = table[x ^ (crc & 0xFF)] ^ (crc >> 8)
    return crc

def _crc24(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFFFF
    for x in mv.tobytes():
        crc = table[x ^ (crc>>16 & 0xFF)] ^ ((crc << 8) & 0xFFFF00)
    return crc

def _crc24r(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFFFF
    for x in mv.tobytes():
        crc = table[x ^ (crc & 0xFF)] ^ (crc >> 8)
    return crc

def _crc32(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFFFFFF
    for x in mv.tobytes():
        crc = table[x ^ ((crc>>24) & 0xFF)] ^ ((crc << 8) & 0xFFFFFF00)
    return crc

def _crc32r(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFFFFFF
    for x in mv.tobytes():
        crc = table[x ^ (crc & 0xFF)] ^ (crc >> 8)
    return crc

def _crc64(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFFFFFFFFFFFFFF
    for x in mv.tobytes():
        crc = table[x ^ ((crc>>56) & 0xFF)] ^ ((crc << 8) & 0xFFFFFFFFFFFFFF00)
    return crc

def _crc64r(data, crc, table):
    mv = _get_buffer_view(data)
    crc &= 0xFFFFFFFFFFFFFFFF
    for x in mv.tobytes():
        crc = table[x ^ (crc & 0xFF)] ^ (crc >> 8)
    return crc

_sizeMap = {
     8 : [_crc8, _crc8r],
    16 : [_crc16, _crc16r],
    24 : [_crc24, _crc24r],
    32 : [_crc32, _crc32r],
    64 : [_crc64, _crc64r],
}

#-----------------------------------------------------------------------------
# Build a mapping of size to struct module type code.  This table is
# constructed dynamically so that it has the best chance of picking the best
# code to use for the platform we are running on.  This should properly adapt
# to 32 and 64 bit machines.

_sizeToTypeCode = {}

for typeCode in 'B H I L Q'.split():
    size = {1:8, 2:16, 4:32, 8:64}.get(struct.calcsize(typeCode), None)
    if size is not None and size not in _sizeToTypeCode:
        _sizeToTypeCode[size] = '256%s' % typeCode

_sizeToTypeCode[24] = _sizeToTypeCode[32]

del typeCode, size

#-----------------------------------------------------------------------------
# The following function validates the parameters of the CRC, namely,
# poly, and initial/final XOR values.
# It returns the size of the CRC (in bits), and "sanitized" initial/final XOR values.

def _verifyParams(poly, initCrc, xorOut):
    sizeBits = _verifyPoly(poly)

    mask = (1<<sizeBits) - 1

    # Adjust the initial CRC to the correct data type (unsigned value).
    initCrc = initCrc & mask

    # Similar for XOR-out value.
    xorOut = xorOut & mask

    return (sizeBits, initCrc, xorOut)

#-----------------------------------------------------------------------------
# The following function returns a Python function to compute the CRC.
#
# It must be passed parameters that are already verified & sanitized by
# _verifyParams().
#
# The returned function calls a low level function that is written in C if the
# extension module could be loaded.  Otherwise, a Python implementation is
# used.
#
# In addition to this function, a list containing the CRC table is returned.

def _mkCrcFun(poly, sizeBits, initCrc, rev, xorOut):
    if rev:
        tableList = _mkTable_r(poly, sizeBits)
        _fun = _sizeMap[sizeBits][1]
    else:
        tableList = _mkTable(poly, sizeBits)
        _fun = _sizeMap[sizeBits][0]

    _table = tableList

    if xorOut == 0:
        def crcfun(data, crc=initCrc, table=_table, fun=_fun):
            return fun(data, crc, table)
    else:
        def crcfun(data, crc=initCrc, table=_table, fun=_fun):
            return xorOut ^ fun(data, xorOut ^ crc, table)

    return crcfun, tableList
