from bt_usb import *
from random import randint
from crypto_toolbox import *
import re
import signal

def signal_handler(sig, frame):
    pass
signal.signal(signal.SIGINT, signal_handler)

def bt_cmp(a, b):
    return re.match(b.lower(), Hid.to_string(a))

class Env:
    def __init__(self):
        self.rand_addr = 'F374DEC0ADDE'
        self.adv_type = '01'  # random
        self.adv_name = '_'
        self.adv_intv_min = '2000'
        self.adv_intv_max = '2800'
        self.local_ltk = ''.join(['{:02x}'.format(randint(0, 255)) for _ in range(16)])
        self.smp_remote_rand_ediv = None
        self.smp_remote_ltk = None
        self.smp_info = {}
        self.smp_local_rand_ediv = ''.join(['{:02x}'.format(randint(0, 255)) for _ in range(10)])
        self.handle = ''

        self.bonded = False
        self.is_reconnect = False
        self.offset = 0
        self.crc = 0
        self.RECV_LE_CONNECTED = '043e130100'
        self.RECV_LE_DISCONNECTED = '0405040040'
        self.CMD_RESET = '01030c00'
        self.CMP_CMP_RESET = '040e0401030c00'
        self.SET_EVENT_MASK = '01010c08ffffffffffffbf3d'
        self.CMP_SET_EVENT_MASK = '040e0401010c00'
        self.LE_SET_EVENT_MASK = '01012008ffff0f0000000000'
        self.CMP_LE_SET_EVENT_MASK = '040e0401012000'
        self.LE_SET_RAND_ADDR = '01052006'+self.rand_addr
        self.CMP_LE_SET_RAND_ADDR = '040e0401052000'
        self.LE_SET_ADV_PARAM = '0106200f'+self.adv_intv_min+self.adv_intv_max+'00'+self.adv_type+'000000000000000700'
        self.CMP_LE_SET_ADV_PARAM = '040e0401062000'
        adv_data = '0319c10302010503031218'+'{:02x}09{}'.format(1+len(self.adv_name), ''.join(['{:02x}'.format(ord(c)) for c in self.adv_name]))
        self.LE_SET_ADV_DATA = '010820'+'{:02x}{:02x}'.format(len(adv_data)//2+1, len(adv_data)//2)+adv_data
        self.CMP_LE_SET_ADV_DATA = '040e0401082000'
        self.LE_SET_ADV_ENABLE = '010a200101'
        self.CMP_LE_SET_ADV_ENABLE = '040e04010a2000'
        self.LE_SET_SCAN_ENABLE = '010c20020100'
        self.CMP_LE_SET_SCAN_ENABLE = '040e04010c2000'
        self.LE_SET_SCAN_DISABLE = '010c20020000'
        self.CMP_LE_SET_SCAN_DISABLE = '040e04010c2000'
        self.RECV_IOS_UNKNOWN_L2CAP = '02....0b0007003a00'
        self.RSP_IOS_UNKNOWN_L2CAP = '0240000e000a0005000100060002003a000000'
        self.RECV_ATT_EXT_MTU = '02....07000300040002....'
        self.RSP_ATT_EXT_MTU = '024000070003000400031700'
        self.SEND_CONN_PARAM_UPDATE_REQ = '02400010000C000500120008000C000C0000000001'
        self.RECV_ADV_REPORT = '043e5f020100'
        self.RECV_L2CAP_PARAM_UPDATE_REQ = '02....10000c000500125f0800'
        self.RSP_L2CAP_PARAM_UPDATE = '0240000a0006000500130202000000'
        self.SEND_SMP_SECURITY_REQ = '0240000600020006000B01'
        self.SEND_SMP_PAIRING_REQ = '0240000B000700060001030001100303'
        self.RECV_SMP_PAIRING_REQ = '02....0b000700060001'
        self.RSP_SMP_PAIRING = '0240200b000700060002030001100101'
        self.RECV_SMP_PAIRING_CFM = '02....15001100060003'
        self.RSP_SMP_PAIRING_CFM = '02402015001100060003'+'00'*16
        self.RECV_SMP_PAIRING_RND = '02....15001100060004'
        self.RSP_SMP_PAIRING_RND = '02402015001100060004'+'00'*16
        self.RECV_STK_REQ = '043e0d05....00000000000000000000'
        self.RSP_RECV_LTK = '011a2012'+'0000'+'00'*16
        self.RSP_RECV_LTK_NEG = '011b2002'+'0000'
        self.RECV_ENC_CHANGE = '04080400....01'
        self.SEND_ENC_INFO = '02....15001100060006'+'00'*16
        self.RECV_ENC_INFO = '02....15001100060006'
        self.SEND_MASTER_ID = '02....0f000b00060007'+'00'*2+'00'*8
        self.RECV_MASTER_ID = '02....0f000b00060007'
        self.SEND_ID_INFO = '02....15001100060008'+'..'*16
        self.RECV_ID_INFO = '02....0f000b00060007'+'..'*16
        self.SEND_ID_ADDR_INFO = '02....0c000800060009'+'..'*7
        self.RECV_ID_ADDR_INFO = '02....0c000800060009'+'..'*7
        self.CMD_START_ENCRYPT = '0119201c....00000000000000000000'+'00'*16

        self.RECV_GATT_GET_ATT_DEV_NAME = '02....0b000700040008........002a'
        self.RSP_GATT_GET_ATT_DEV_NAME = '02....090005000400010806000a'
        self.RECV_GATT_FIND_PnP_ID = '02....0b000700040008........502a'
        self.RSP_GATT_FIND_PnP_ID = '02....090005000400010801000a'
        self.RECV_GATT_READ_ALL_GROUP_TYPE = '02....0b0007000400100100ffff0028'
        # 1 - service
        # 2~3 - report map
        # 4~7 - report
        # 8~b - report
        # 0c~0d - info
        #     ''' Report map:
        #     05010906a101050719e029e715002501750195088102
        #     95017508810195067508150025650507190029658100
        #     0905150026ff0075089502b102c0
        #     05010902a10185010901a10005091901290815002501
        #     75019508810205011608ff26ff007510950209300931
        #     81061581257f7508950109388106c0c0
        #     '''
        self.RSP_GATT_READ_ALL_GROUP_TYPE = '02....0c00080004001106' + '01000d001218'
        self.RECV_GATT_READ_GROUP_TYPE_AGAIN = '02....0b000700040010....ffff0028'
        self.RSP_GATT_READ_GROUP_TYPE_AGAIN = '02....090005000400011010000a'  # not found
        self.RECV_GATT_READ_INCLUDE = '02....0b0007000400080100....0228'
        self.RSP_GATT_READ_INCLUDE = '02....090005000400010801000a'  # not found
        self.RECV_GATT_FIND_CHAR_1 = '02....0b0007000400080100..000328'
        self.RSP_GATT_FIND_CHAR_1 = '02....1b0017000400'+'0907'+'02000203004b2a'+'04001205004d2a'+'08001209004d2a'
        self.RECV_GATT_FIND_CHAR_2 = '02....0b000700040008((09)|(0a))00..000328'
        self.RSP_GATT_FIND_CHAR_2 = '02....0d0009000400'+'0907'+'0c00020d004a2a'
        self.RECV_GATT_FIND_CHAR_3 = '02....0b000700040008((0d)|(0e))00..000328'
        self.RSP_GATT_FIND_CHAR_3 = '02....09000500040001080e000a'  # not found
        self.RECV_GATT_FIND_CHAR_4 = '02....0b0007000400080f00..000328'  # adapt android
        self.RSP_GATT_FIND_CHAR_4 = '02....09000500040001080e000a'
        self.RECV_GATT_FIND_INFO_1 = '02....09000500040004'+'06000700'
        self.RSP_GATT_FIND_INFO_1 = '02....0e000a00040005'+'01'+'06000229'+'07000829'
        self.RECV_GATT_FIND_INFO_2 = '02....09000500040004'+'0a000b00'
        self.RSP_GATT_FIND_INFO_2 = '02....0e000a00040005'+'01'+'0a000229'+'0b000829'
        self.RECV_GATT_READ_REPORT_MAP = '02....0700030004000a'+'0300'
        self.RSP_GATT_READ_REPORT_MAP = '02....1b00170004000b'
        self.RECV_GATT_READ_REPORT_MAP_CTN = '02....0900050004000c'+'0300'+'..00'
        self.RSP_GATT_READ_REPORT_DATA = '05010906a1018501050719e029e715002501750195088102' \
                                         '95017508810195067508150025650507190029658100' \
                                         '0905150026ff0075089502b102c0' \
                                         '05010902a10185020901a10005091901290815002501' \
                                         '75019508810205011608ff26ff007510950209300931' \
                                         '81061581257f7508950109388106c0c0'
        self.report_data_offset = 0
        self.RSP_GATT_READ_REPORT_MAP_HEADER = '02....1b00170004000d'
        self.RECV_GATT_READ_REPORT_REF1 = '02....0700030004000a'+'0700'
        self.RSP_GATT_READ_REPORT_REF1 = '02....0700030004000b'+'0101'
        self.RECV_GATT_READ_REPORT_REF2 = '02....0700030004000a'+'0b00'
        self.RSP_GATT_READ_REPORT_REF2 = '02....0700030004000b'+'0201'
        self.RECV_GATT_READ_REPORT_INFO = '02....0700030004000a'+'0d00'
        self.RSP_GATT_READ_REPORT_INFO = '02....0900050004000b'+'00000002'
        self.RECV_GATT_WRITE_DES1 = '02....09000500040012'+'((06)|(0a))00'+'0100'
        self.RSP_GATT_WRITE_DES1_INSUFF = '0208200900050004000112080005'
        self.RSP_GATT_WRITE_DES1 = '02....05000100040013'
        self.SEND_GATT_KEY = '02....0f000b0004001B'+'0500'+'0000000000000000'
        self.SEND_GATT_MOUSE_MOVE = '02....0f000b0004001B'+'0900'+'000100010000'

        self.RECV_RECONNECT_LTK_REQ = '043e0d05'+'..'*8+'....'
        self.RSP_RECONNECT_LTK = '011a2012'+'0000'+'00'*16
        self.load()

    def save(self):
        rand_ediv = self.smp_local_rand_ediv[2*2:]+self.smp_local_rand_ediv[:2*2]
        if rand_ediv not in self.local_ltk:
            self.smp_info[rand_ediv] = self.local_ltk
            with open('smp.dat', 'w', encoding='utf-8') as f:
                for k, v in self.smp_info.items():
                    f.write(k + v + '\n')
                f.close()

    def load(self):
        try:
            with open('smp.dat', 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    k = line[:10*2]
                    v = line[10*2:(10+16)*2]
                    self.smp_info[k] = v
                f.close()
        except FileNotFoundError:
            pass

class Hid:
    def __init__(self, param):
        self.env = param
        self.bt = BtUsb(self.bt_cb, self.env, rec_log=False, dump_log=False)

    @staticmethod
    def to_string(data):
        return ''.join('{:02x}'.format(x) for x in data)

    def send(self, data):
        return self.bt.send(bytes.fromhex(data))

    def bt_cb(self, data, e):
        if bt_cmp(data, e.CMP_CMP_RESET):
            self.env.is_reconnect = False
            self.env.smp_remote_rand_ediv = None
            self.env.smp_remote_ltk = None
            self.send(e.SET_EVENT_MASK)
        elif bt_cmp(data, e.CMP_SET_EVENT_MASK):
            self.send(e.LE_SET_EVENT_MASK)
        elif bt_cmp(data, e.CMP_LE_SET_EVENT_MASK):
            self.send(e.LE_SET_ADV_PARAM)
        elif bt_cmp(data, e.CMP_LE_SET_ADV_PARAM):
            self.send(e.LE_SET_RAND_ADDR)
        elif bt_cmp(data, e.CMP_LE_SET_RAND_ADDR):
            self.send(e.LE_SET_ADV_DATA)
        elif bt_cmp(data, e.CMP_LE_SET_ADV_DATA):
            self.send(e.LE_SET_ADV_ENABLE)
        elif bt_cmp(data, e.CMP_LE_SET_ADV_ENABLE):
            print("Advertise enabled !")
        elif bt_cmp(data, e.RECV_LE_CONNECTED):
            self.send(e.SEND_CONN_PARAM_UPDATE_REQ)
            self.send(e.SEND_SMP_SECURITY_REQ)
            print("Device connected !")
            self.env.handle = self.to_string(data[5:7])
            self.env.init_type = self.to_string(data[8:9])
            self.env.init_addr = self.to_string(data[9:15])
        elif bt_cmp(data, e.RECV_LE_DISCONNECTED):
            print("Device disconnected !")
            self.send(e.CMD_RESET)
        elif bt_cmp(data, e.RECV_IOS_UNKNOWN_L2CAP):
            self.send(e.RSP_IOS_UNKNOWN_L2CAP)
        elif bt_cmp(data, e.RECV_ATT_EXT_MTU):
            print("MTU exchanged !")
            self.send(e.RSP_ATT_EXT_MTU)
        elif bt_cmp(data, e.RECV_SMP_PAIRING_REQ):
            self.env.smp_req_cmd = self.to_string(data[-7:])
            self.env.smp_rsp_cmd = e.RSP_SMP_PAIRING[-7*2:]
            self.send('02'+self.env.handle+e.RSP_SMP_PAIRING[3*2:])
        elif bt_cmp(data, e.RECV_SMP_PAIRING_CFM):
            self.env.smp_local_rnd = self.to_string([randint(0, 255) for _ in range(16)])
            self.env.smp_remote_cfm = self.to_string(data[-16:])
            cfm_value = btc_confirm_value(
                b'\x00' * 16,  # tk
                brev(hexstr2bytes(self.env.smp_local_rnd)),  # rand
                brev(hexstr2bytes(self.env.smp_req_cmd)),  # req_cmd
                brev(hexstr2bytes(self.env.smp_rsp_cmd)),  # rsp_cmd
                hexstr2bytes(self.env.init_type),  # iat
                hexstr2bytes(self.env.adv_type),  # rat
                brev(hexstr2bytes(self.env.init_addr)),  # ia
                brev(hexstr2bytes(self.env.rand_addr)),  # ra
            )
            self.env.smp_local_cfm = self.to_string(brev(cfm_value))
            self.send('02'+self.env.handle+e.RSP_SMP_PAIRING_CFM[3*2:-16*2]+self.env.smp_local_cfm)
        elif bt_cmp(data, e.RECV_SMP_PAIRING_RND):
            self.env.smp_remote_rnd = self.to_string(data[-16:])
            self.send('02'+self.env.handle+e.RSP_SMP_PAIRING_RND[3*2:-16*2]+self.env.smp_local_rnd)
        elif bt_cmp(data, e.RECV_STK_REQ):
            self.env.local_stk = self.to_string(
                brev(btc_s1(b'\x00'*16,
                            brev(bytes.fromhex(self.env.smp_local_rnd)),
                            brev(bytes.fromhex(self.env.smp_remote_rnd)))))
            self.send(e.RSP_RECV_LTK[:4*2]+self.env.handle+self.env.local_stk)
        elif bt_cmp(data, e.RECV_ENC_CHANGE):
            self.env.bonded = True
            if not self.env.is_reconnect:
                self.send('02'+self.env.handle+e.SEND_ENC_INFO[3*2:-16*2]+self.env.local_ltk)
                self.send('02'+self.env.handle+e.SEND_MASTER_ID[3*2:-10*2]+self.env.smp_local_rand_ediv)
                self.env.save()
        elif bt_cmp(data, e.RECV_ENC_INFO):
            self.env.smp_remote_ltk = self.to_string(data[-16:])
        elif bt_cmp(data, e.RECV_MASTER_ID):
            self.env.smp_remote_rand_ediv = self.to_string(data[-10:])
        elif bt_cmp(data, e.RECV_GATT_GET_ATT_DEV_NAME):
            self.send('02'+self.env.handle+e.RSP_GATT_GET_ATT_DEV_NAME[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_PnP_ID):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_PnP_ID[3*2:])
        elif bt_cmp(data, e.RECV_GATT_READ_ALL_GROUP_TYPE):
            self.send('02'+self.env.handle+e.RSP_GATT_READ_ALL_GROUP_TYPE[3*2:])
        elif bt_cmp(data, e.RECV_GATT_READ_GROUP_TYPE_AGAIN):
            self.send('02'+self.env.handle+e.RSP_GATT_READ_GROUP_TYPE_AGAIN[3*2:])
        elif bt_cmp(data, e.RECV_GATT_READ_INCLUDE):
            self.send('02'+self.env.handle+e.RSP_GATT_READ_INCLUDE[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_CHAR_1):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_CHAR_1[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_CHAR_2):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_CHAR_2[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_CHAR_3):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_CHAR_3[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_CHAR_4):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_CHAR_4[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_INFO_1):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_INFO_1[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_INFO_2):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_INFO_2[3*2:])
        elif bt_cmp(data, e.RECV_GATT_READ_REPORT_MAP):
            self.send('02'+self.env.handle+e.RSP_GATT_READ_REPORT_MAP[3*2:] +
                      e.RSP_GATT_READ_REPORT_DATA[e.report_data_offset:e.report_data_offset+22*2])
            e.report_data_offset += 22*2
        elif bt_cmp(data, e.RECV_GATT_READ_REPORT_MAP_CTN):
            remain = len(e.RSP_GATT_READ_REPORT_DATA) - e.report_data_offset
            if remain >= 22*2:
                self.send('02'+self.env.handle + e.RSP_GATT_READ_REPORT_MAP_HEADER[3*2:] +
                          e.RSP_GATT_READ_REPORT_DATA[e.report_data_offset:e.report_data_offset+22*2])
                e.report_data_offset += 22*2
            else:
                self.send('02'+self.env.handle
                          + '{:02x}'.format(remain//2+5)+'00'+'{:02x}'.format(remain//2+1)+'00'
                          + e.RSP_GATT_READ_REPORT_MAP_HEADER[7*2:] +
                          e.RSP_GATT_READ_REPORT_DATA[e.report_data_offset:])
                e.report_data_offset = 0
        elif bt_cmp(data, e.RECV_GATT_READ_REPORT_REF1):
            self.send('02'+self.env.handle+e.RSP_GATT_READ_REPORT_REF1[3*2:])
        elif bt_cmp(data, e.RECV_GATT_READ_REPORT_REF2):
            self.send('02'+self.env.handle+e.RSP_GATT_READ_REPORT_REF2[3*2:])
        elif bt_cmp(data, e.RECV_GATT_READ_REPORT_INFO):
            self.send('02'+self.env.handle+e.RSP_GATT_READ_REPORT_INFO[3*2:])
        elif bt_cmp(data, e.RECV_GATT_WRITE_DES1):
            if self.env.bonded:
                self.send('02'+self.env.handle+e.RSP_GATT_WRITE_DES1[3*2:])
            else:
                self.send('02'+self.env.handle+e.RSP_GATT_WRITE_DES1_INSUFF[3*2:])
        elif bt_cmp(data, e.RECV_RECONNECT_LTK_REQ):
            self.env.is_reconnect = True
            self.env.smp_remote_rand_ediv = self.to_string(data[6:])
            if self.env.smp_remote_rand_ediv in self.env.smp_info:
                self.send(e.RSP_RECV_LTK[:4*2]+self.env.handle +
                          self.env.smp_info[self.env.smp_remote_rand_ediv])
            else:
                self.send(e.RSP_RECV_LTK[:4*2]+self.env.handle + '00'*16)


    def start(self):
        self.send(self.env.CMD_RESET)

key_map = {
    30: 0x04,  # Keyboard a and A
    48: 0x05,  # Keyboard b and B
    46: 0x06,  # Keyboard c and C
    32: 0x07,  # Keyboard d and D
    18: 0x08,  # Keyboard e and E
    33: 0x09,  # Keyboard f and F
    34: 0x0a,  # Keyboard g and G
    35: 0x0b,  # Keyboard h and H
    23: 0x0c,  # Keyboard i and I
    36: 0x0d,  # Keyboard j and J
    37: 0x0e,  # Keyboard k and K
    38: 0x0f,  # Keyboard l and L
    50: 0x10,  # Keyboard m and M
    49: 0x11,  # Keyboard n and N
    24: 0x12,  # Keyboard o and O
    25: 0x13,  # Keyboard p and P
    16: 0x14,  # Keyboard q and Q
    19: 0x15,  # Keyboard r and R
    31: 0x16,  # Keyboard s and S
    20: 0x17,  # Keyboard t and T
    22: 0x18,  # Keyboard u and U
    47: 0x19,  # Keyboard v and V
    17: 0x1a,  # Keyboard w and W
    45: 0x1b,  # Keyboard x and X
    21: 0x1c,  # Keyboard y and Y
    44: 0x1d,  # Keyboard z and Z
    2: 0x1e,  # Keyboard 1 and !
    3: 0x1f,  # Keyboard 2 and @
    4: 0x20,  # Keyboard 3 and #
    5: 0x21,  # Keyboard 4 and $
    6: 0x22,  # Keyboard 5 and %
    7: 0x23,  # Keyboard 6 and ^
    8: 0x24,  # Keyboard 7 and &
    9: 0x25,  # Keyboard 8 and *
    10: 0x26,  # Keyboard 9 and (
    11: 0x27,  # Keyboard 0 and )
    28: 0x28,  # Keyboard Return (ENTER)
    1: 0x29,  # Keyboard ESCAPE
    14: 0x2a,  # Keyboard DELETE (Backspace)
    15: 0x2b,  # Keyboard Tab
    57: 0x2c,  # Keyboard Space bar
    12: 0x2d,  # Keyboard - and _
    13: 0x2e,  # Keyboard = and +
    26: 0x2f,  # Keyboard [ and {
    27: 0x30,  # Keyboard ] and }
    43: 0x31,  # Keyboard \ and |
    39: 0x33,  # Keyboard ; and :
    40: 0x34,  # Keyboard ' and "
    41: 0x35,  # Keyboard ` and ~
    51: 0x36,  # Keyboard , and <
    52: 0x37,  # Keyboard . and >
    53: 0x38,  # Keyboard / and ?
    58: 0x39,  # Keyboard Caps Lock
    59: 0x3a,  # Keyboard F1
    60: 0x3b,  # Keyboard F2
    61: 0x3c,  # Keyboard F3
    62: 0x3d,  # Keyboard F4
    63: 0x3e,  # Keyboard F5
    64: 0x3f,  # Keyboard F6
    65: 0x40,  # Keyboard F7
    66: 0x41,  # Keyboard F8
    67: 0x42,  # Keyboard F9
    68: 0x43,  # Keyboard F10
    69: 0x44,  # Keyboard F11
    70: 0x45,  # Keyboard F12
    99: 0x46,  # Keyboard Print Screen
    110: 0x49,  # Keyboard Insert
    102: 0x4a,  # Keyboard Home
    104: 0x4b,  # Keyboard Page Up
    111: 0x4c,  # Keyboard Delete Forward
    107: 0x4d,  # Keyboard End
    109: 0x4e,  # Keyboard Page Down
    106: 0x4f,  # Keyboard Right Arrow
    105: 0x50,  # Keyboard Left Arrow
    108: 0x51,  # Keyboard Down Arrow
    103: 0x52,  # Keyboard Up Arrow
    29: 0xe0,  # Keyboard Left Control
    42: 0xe1,  # Keyboard Left Shift
    56: 0xe2,  # Keyboard Left Alt
    125: 0xe3,  # Keyboard Left GUI
    97: 0xe4,  # Keyboard Right Control
    54: 0xe5,  # Keyboard Right Shift
    100: 0xe6,  # Keyboard Right Alt
}


def pressed_keys(code, value, comb_key):
    if value == 1:
        if code in key_map:
            # hid.send('02'+env.handle+env.SEND_GATT_KEY[3*2:-8*2] + '00' * 8)
            hid.send('02'+env.handle+env.SEND_GATT_KEY[3*2:-8*2] + '{:02x}00{:02x}0000000000'.
                     format(comb_key, key_map[code]))
    elif value == 0:
        hid.send('02'+env.handle+env.SEND_GATT_KEY[3*2:-8*2] + '00' * 8)
        print('\r' + ' ' * 8 + '\r', end='')


class keyboard_hook:
    def __init__(self, keyboard_cb, keyboard_dev='/dev/input/event3', mouse_dev='/dev/input/event8'):
        self.cb = keyboard_cb
        self.dev_k = keyboard_dev
        self.dev_m = mouse_dev
        self.comb_key = 0
        self.paused = False
    def run(self):
        import struct
        fmt = 'llHHI'
        event_size = struct.calcsize(fmt)
        keyboard_file = open(self.dev_k, "rb")
        event = keyboard_file.read(event_size)
        while event:
            (tv_sec, tv_usec, type, code, value) = struct.unpack(fmt, event)
            if type == 1 and (code != 0 or value != 0):
                # Bit 7 Bit 6 Bit 5  Bit 4 Bit 3 Bit 2 Bit 1  Bit 0
                # RGUI  RAlt  RShift RCtrl LGUI  LAlt  LShift LCtrl
                if value == 1:
                    if code == 29:
                        self.comb_key |= (1 << 0)
                    elif code == 42:
                        self.comb_key |= (1 << 1)
                    elif code == 56:
                        self.comb_key |= (1 << 2)
                    elif code == 125:
                        self.comb_key |= (1 << 3)
                    elif code == 97:
                        self.comb_key |= (1 << 4)
                    elif code == 54:
                        self.comb_key |= (1 << 5)
                    elif code == 100:
                        self.comb_key |= (1 << 6)
                elif value == 0:
                    if code == 29:
                        self.comb_key &= ~(1 << 0)
                    elif code == 42:
                        self.comb_key &= ~(1 << 1)
                    elif code == 56:
                        self.comb_key &= ~(1 << 2)
                    elif code == 125:
                        self.comb_key &= ~(1 << 3)
                    elif code == 97:
                        self.comb_key &= ~(1 << 4)
                    elif code == 54:
                        self.comb_key &= ~(1 << 5)
                    elif code == 100:
                        self.comb_key &= ~(1 << 6)
                if (self.comb_key & (1 << 3)) != 0 and code == 42 and value == 1:  # GUI + LeftShift
                    self.paused = not self.paused
                    print('Keyboard paused:', self.paused)
                if not self.paused:
                    self.cb(code, value, self.comb_key)
            event = keyboard_file.read(event_size)


if __name__ == '__main__':
    env = Env()
    hid = Hid(env)
    hid.start()
    keyboard_hook(pressed_keys).run()
