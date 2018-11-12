from bt_usb import *
from struct import pack
import binascii

offset = 0
crc = 0

RECV_LE_CONNECTED = b'\x04\x3e\x13\x01\x00'
RECV_LE_DISCONNECTED = b'\x04\x05\x04\x00\x40'

CMD_RESET = b'\x01\x03\x0c\x00'
CMP_RESET = b'\x04\x0e\x04\x01\x03\x0c\x00'

SET_EVENT_MASK = b'\x01\x01\x0c\x08\xff\xff\xff\xff\xff\xff\xbf\x3d'
CMP_SET_EVENT_MASK = b'\x04\x0e\x04\x01\x01\x0c\x00'

LE_SET_EVENT_MASK = b'\x01\x01\x20\x08\xff\xff\x0f\x00\x00\x00\x00\x00'
CMP_LE_SET_EVENT_MASK = b'\x04\x0e\x04\x01\x01\x20\x00'

LE_SET_ADV_PARAM = b'\x01\x06\x20\x0f\x40\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00'
CMP_LE_SET_ADV_PARAM = b'\x04\x0e\x04\x01\x06\x20\x00'

LE_SET_ADV_DATA = b'\x01\x08\x20\x20\x19\x0b\x09\x55\x53\x42\x20\x44\x6f\x6e\x67\x6c\x65\x03\x19\xc2\x03\x02\x01\x06\x03\x03\x12\x18\x00\x00\x00\x00\x00\x00\x00\x00'
CMP_LE_SET_ADV_DATA = b'\x04\x0e\x04\x01\x08\x20\x00'

LE_SET_ADV_ENABLE = b'\x01\x0a\x20\x01\x01'
CMP_LE_SET_ADV_ENABLE = b'\x04\x0e\x04\x01\x0a\x20\x00'

LE_SET_SCAN_ENABLE = b'\x01\x0c\x20\x02\x01\x00'
CMP_LE_SET_SCAN_ENABLE = b'\x04\x0e\x04\x01\x0c\x20\x00'

LE_SET_SCAN_DISABLE = b'\x01\x0c\x20\x02\x00\x00'
CMP_LE_SET_SCAN_DISABLE = b'\x04\x0e\x04\x01\x0c\x20\x00'

RECV_IOS_UNKNOWN_L2CAP = b'\x02\x5f\x5f\x0b\x00\x07\x00\x3a\x00'
RSP_IOS_UNKNOWN_L2CAP = b'\x02\x40\x00\x0e\x00\x0a\x00\x05\x00\x01\x00\x06\x00\x02\x00\x3a\x00\x00\x00'

RECV_ATT_EXT_MTU = b'\x02\x5f\x5f\x07\x00\x03\x00\x04\x00\x02\x5f\x5f'
RSP_ATT_EXT_MTU = b'\x02\x40\x00\x07\x00\x03\x00\x04\x00\x03\x17\x00'

RECV_GATT_GET_SERVICE_1 = b'\x02\x5f\x5f\x0b\x00\x07\x00\x04\x00\x10\x01\x00\xff\xff\x00\x28'
RSP_GATT_GET_SERVICE_1 = b'\x02\x40\x00\x0C\x00\x08\x00\x04\x00\x11\x06\x01\x00\x07\x00\x59\xFE'

RECV_GATT_GET_SERVICE_2 = b'\x02\x5f\x5f\x0b\x00\x07\x00\x04\x00\x10\x08\x00\xff\xff\x00\x28'
RSP_GATT_GET_SERVICE_2 = b'\x02\x40\x00\x09\x00\x05\x00\x04\x00\x01\x10\x08\x00\x0a'

RECV_GATT_GET_INCLUDE_SERVICE = b'\x02\x5f\x5f\x0b\x00\x07\x00\x04\x00\x08\x5f\x5f\x5f\x5f\x02\x28'
RSP_GATT_GET_INCLUDE_SERVICE = b'\x02\x40\x00\x09\x00\x05\x00\x04\x00\x01\x08\x06\x00\x0a'

RECV_GATT_GET_SERVICE_3 = b'\x02\x5f\x5f\x0b\x00\x07\x00\x04\x00\x08\x01\x00\x07\x00\x03\x28'
RSP_GATT_GET_SERVICE_3 = b'\x02\x40\x00\x1b\x00\x17\x00\x04\x00\x09\x15\x02\x00\x18\x03\x00\x50\xEA\xDA\x30\x88\x83\xB8\x9F\x60\x4F\x15\xF3\x01\x00\xC9\x8E'

RECV_GATT_GET_SERVICE_3_1_IPHONE = b'\x02\x5f\x5f\x0b\x00\x07\x00\x04\x00\x08\x04\x00\x07\x00\x03\x28'
RECV_GATT_GET_SERVICE_3_1_ANDROID = b'\x02\x5f\x5f\x0b\x00\x07\x00\x04\x00\x08\x03\x00\x07\x00\x03\x28'
RSP_GATT_GET_SERVICE_3_1 = b'\x02\x40\x00\x1b\x00\x17\x00\x04\x00\x09\x15\x05\x00\x14\x06\x00\x50\xEA\xDA\x30\x88\x83\xB8\x9F\x60\x4F\x15\xF3\x02\x00\xC9\x8E'

RECV_GATT_GET_SERVICE_3_2 = b'\x02\x5f\x5f\x0b\x00\x07\x00\x04\x00\x08\x5f\x00\x5f\x00\x03\x28'
RSP_GATT_GET_SERVICE_3_2 = b'\x02\x40\x00\x09\x00\x05\x00\x04\x00\x01\x08\x06\x00\x0a'

RECV_GATT_GET_SERVICE_4_IPHONE = b'\x02\x5f\x5f\x09\x00\x05\x00\x04\x00\x04\x04\x00\x04\x00'
RECV_GATT_GET_SERVICE_4_ANDROID = b'\x02\x5f\x5f\x09\x00\x05\x00\x04\x00\x01\x07\x00\x04\x00'
RSP_GATT_GET_SERVICE_4 = b'\x02\x40\x00\x0a\x00\x06\x00\x04\x00\x05\x01\x04\x00\x02\x29'

RECV_GATT_GET_SERVICE_5_IPHONE = b'\x02\x5f\x5f\x09\x00\x05\x00\x04\x00\x04\x07\x00\x07\x00'
RECV_GATT_GET_SERVICE_5_ANDROID = b'\x02\x5f\x5f\x09\x00\x05\x00\x04\x00\x04\x06\x00\x07\x00'
RSP_GATT_GET_SERVICE_5 = b'\x02\x40\x00\x0a\x00\x06\x00\x04\x00\x05\x01\x07\x00\x02\x29'

RECV_GATT_READ_CHAR = b'\x02\x5f\x5f\x07\x00\x03\x00\x04\x00\x0a\x03\x00'
RSP_GATT_READ_CHAR = b'\x02\x40\x00\x0f\x00\x0b\x00\x04\x00\x0b\x4d\x79\x54\x65\x73\x74\x44\x61\x74\x61'

RECV_GATT_WRITE_CTRL_POINT = b'\x02\x5f\x5f\x5f\x00\x5f\x00\x04\x00\x12\x03\x00'
RSP_GATT_WRITE_CTRL_POINT = b'\x02\x40\x00\x05\x00\x01\x00\x04\x00\x13'

RECV_GATT_WRITE_CMD_DATA = b'\x02\x5f\x5f\x5f\x00\x5f\x00\x04\x00\x52\x06\x00'

RECV_GATT_WRITE_CHAR = b'\x02\x5f\x5f\x5f\x5f\x5f\x5f\x04\x00\x12'
RSP_GATT_WRITE_CHAR = b'\x02\x40\x00\x05\x00\x01\x00\x04\x00\x13'

RECV_GATT_READ = b'\x02\x5f\x5f\x07\x00\x03\x00\x04\x00\x0a\x5f\x00'
RSP_GATT_READ = b'\x02\x40\x00\x07\x00\x03\x00\x04\x00\x0b\x00\x00'

SEND_GATT_READ_REQ = b'\x02\x40\x00\x07\x00\x03\x00\x04\x00\x0a\x02\x00'

SEND_SMP_PAIRING_REQ = b'\x02\x40\x00\x0B\x00\x07\x00\x06\x00\x01\x03\x00\x01\x10\x03\x03'

SEND_CONN_PARAM_UPDATE_REQ = b'\x02\x40\x00\x10\x00\x0C\x00\x05\x00\x12\x00\x08\x00\x0C\x00\x0C\x00\x00\x00\x00\x01'

RECV_ADV_REPORT = b'\x04\x3e\x5f\x02\x01\x00'

RECV_L2CAP_PARAM_UPDATE_REQ = b'\x02\x5f\x5f\x10\x00\x0c\x00\x05\x00\x12\x5f\x08\x00'
RSP_L2CAP_PARAM_UPDATE = b'\x02\x40\x00\x0a\x00\x06\x00\x05\x00\x13\x02\x02\x00\x00\x00'


def bt_cmp(a, b):
    for (ia, ib) in zip(a[:len(b)], b):
        if ib != 0x5f and ia != ib:
            return 0
    return 1


def crc32_compute(d, l, c):
    return binascii.crc32(d, c)


def cb(data, param):
    if bt_cmp(data, CMP_RESET):
        bt_usb.send(SET_EVENT_MASK)
    elif bt_cmp(data, CMP_SET_EVENT_MASK):
        bt_usb.send(LE_SET_EVENT_MASK)
    elif bt_cmp(data, CMP_LE_SET_EVENT_MASK):
        bt_usb.send(LE_SET_ADV_PARAM)
    elif bt_cmp(data, CMP_LE_SET_ADV_PARAM):
        bt_usb.send(LE_SET_ADV_DATA)
    elif bt_cmp(data, CMP_LE_SET_ADV_DATA):
        bt_usb.send(LE_SET_ADV_ENABLE)
    elif bt_cmp(data, CMP_LE_SET_ADV_ENABLE):
        print("Advertise enabled !")
    elif bt_cmp(data, RECV_LE_CONNECTED):
        bt_usb.send(SEND_CONN_PARAM_UPDATE_REQ)
        print("Device connected !")
    elif bt_cmp(data, RECV_LE_DISCONNECTED):
        print("Device disconnected !")
        bt_usb.send(CMD_RESET)
    elif bt_cmp(data, RECV_IOS_UNKNOWN_L2CAP):
        bt_usb.send(RSP_IOS_UNKNOWN_L2CAP)
    elif bt_cmp(data, RECV_ATT_EXT_MTU):
        print("MTU exchanged !")
        bt_usb.send(RSP_ATT_EXT_MTU)
    elif bt_cmp(data, RECV_GATT_GET_INCLUDE_SERVICE):
        bt_usb.send(RSP_GATT_GET_INCLUDE_SERVICE)
    elif bt_cmp(data, RECV_GATT_GET_SERVICE_1):
        bt_usb.send(RSP_GATT_GET_SERVICE_1)
    elif bt_cmp(data, RECV_GATT_GET_SERVICE_2):
        bt_usb.send(RSP_GATT_GET_SERVICE_2)
    elif bt_cmp(data, RECV_GATT_GET_SERVICE_3):
        bt_usb.send(RSP_GATT_GET_SERVICE_3)
    elif bt_cmp(data, RECV_GATT_GET_SERVICE_3_1_IPHONE) or bt_cmp(data, RECV_GATT_GET_SERVICE_3_1_ANDROID):
        bt_usb.send(RSP_GATT_GET_SERVICE_3_1)
    elif bt_cmp(data, RECV_GATT_GET_SERVICE_3_2):
        bt_usb.send(RSP_GATT_GET_SERVICE_3_2)
    elif bt_cmp(data, RECV_GATT_GET_SERVICE_4_IPHONE) or bt_cmp(data, RECV_GATT_GET_SERVICE_4_ANDROID):
        bt_usb.send(RSP_GATT_GET_SERVICE_4)
    elif bt_cmp(data, RECV_GATT_GET_SERVICE_5_IPHONE) or bt_cmp(data, RECV_GATT_GET_SERVICE_5_ANDROID):
        bt_usb.send(RSP_GATT_GET_SERVICE_5)
    elif bt_cmp(data, RECV_GATT_READ_CHAR):
        print("GATT_READ_CHAR !")
        bt_usb.send(RSP_GATT_READ_CHAR)
    elif bt_cmp(data, RECV_GATT_WRITE_CTRL_POINT):
        print("GATT_WRITE CONTROL POINT !")
        bt_usb.send(RSP_GATT_WRITE_CTRL_POINT)
    elif bt_cmp(data, RECV_GATT_WRITE_CHAR):
        print("GATT_WRITE !")
        bt_usb.send(RSP_GATT_WRITE_CHAR)
    elif bt_cmp(data, RECV_GATT_READ):
        print("GATT_READ_DESC !")
        bt_usb.send(RSP_GATT_READ)

    if bt_cmp(data, RECV_GATT_WRITE_CMD_DATA):
        length = len(data)
        param[1] = crc32_compute(data[12:], length-12, param[1])
        param[0] += length-12

    if bt_cmp(data, RECV_GATT_WRITE_CTRL_POINT):
        if data[12:14] == b'\x06\x01' or data[12:14] == b'\x06\x02':  # select
            tmp = b'\x02\x40\x00\x16\x00\x12\x00\x04\x00\x1b\x03\x00\x60\x06\x01'
            bt_usb.send(pack('<%dsIII' % (len(tmp),), tmp, (1 << 20), param[0], param[1]))
        elif data[12:14] == b'\x01\x01' or data[12:14] == b'\x01\x02':  # create
            tmp = b'\x02\x40\x00\x0a\x00\x06\x00\x04\x00\x1b\x03\x00\x60\x01\x01'
            bt_usb.send(tmp)
            param[0] = 0
            param[1] = 0
        elif data[12:13] == b'\x02':
            tmp = b'\x02\x40\x00\x0a\x00\x06\x00\x04\x00\x1b\x03\x00\x60\x02\x01'
            bt_usb.send(tmp)
        elif data[12:13] == b'\x03':
            tmp = b'\x02\x40\x00\x12\x00\x0e\x00\x04\x00\x1b\x03\x00\x60\x03\x01'
            bt_usb.send(pack('<%dsII' % (len(tmp),), tmp, param[0], param[1]))
        elif data[12:13] == b'\x04':
            tmp = b'\x02\x40\x00\x0a\x00\x06\x00\x04\x00\x1b\x03\x00\x60\x04\x01'
            bt_usb.send(tmp)


if __name__ == '__main__':
    _param = [0, 0]
    bt_usb = BtUsb(cb, _param, dump_log=True)
    bt_usb.send(b'\x01\x03\x0c\x00')
