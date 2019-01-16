from bt_usb import *
from random import randint
from crypto_toolbox import *
import re

def bt_cmp(a, b):
    if re.match(b.lower(), Hid.to_string(a)):
        return 1
    else:
        return 0

class Env:
    def __init__(self):
        self.rand_addr = 'F374DEC0ADDE'
        self.adv_type = '01'  # random
        self.adv_name = '_'
        self.adv_intv_min = '2000'
        self.adv_intv_max = '2800'
        self.local_ltk = ''.join(['{:02x}'.format(randint(0, 255)) for _ in range(16)])
        self.local_irk = ''.join(['{:02x}'.format(randint(0, 255)) for _ in range(16)])
        self.irk = 'FEDCBA9876543210FEDCBA9876543210'
        self.smp_remote_rand_ediv = None
        self.smp_local_rand_ediv = ''.join(['{:02x}'.format(randint(0, 255)) for _ in range(10)])
        self.handle = ''

        self.bonded = False
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
        self.RSP_SMP_PAIRING = '0240200b000700060002030001100303'
        self.RECV_SMP_PAIRING_CFM = '02....15001100060003'
        self.RSP_SMP_PAIRING_CFM = '02402015001100060003'+'00'*16
        self.RECV_SMP_PAIRING_RND = '02....15001100060004'
        self.RSP_SMP_PAIRING_RND = '02402015001100060004'+'00'*16
        self.RECV_LTK_REQ = '043e0d05....00000000000000000000'
        self.RSP_RECV_LTK = '011a2012'+'0000'+'00'*16
        self.RSP_RECV_LTK_NEG = '011b2002'+'0000'
        self.RECV_ENC_CHANGE = '04080400....01'
        self.SEND_ENC_INFO = '02....15001100060006'+'00'*16
        self.RECV_ENC_INFO = self.SEND_ENC_INFO
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
        #
        # 1 - service
        # 2~3 - report map
        # 4~7 - report
        # 8~11 - report
        # 12~13 - info
        # 14~15 - ctrl
        self.RSP_GATT_READ_ALL_GROUP_TYPE = '02....0c0008000400110601000F00' + '1218'  # 1 service with 1~15 handle
        self.RECV_GATT_READ_GROUP_TYPE_AGAIN = '02....0b0007000400101000ffff0028'
        self.RSP_GATT_READ_GROUP_TYPE_AGAIN = '02....090005000400011010000a'  # not found
        self.RECV_GATT_READ_INCLUDE = '02....0b0007000400080100....0228'
        self.RSP_GATT_READ_INCLUDE = '02....090005000400010801000a'  # not found
        self.RECV_GATT_FIND_CHAR_1 = '02....0b0007000400080100..000328'
        self.RSP_GATT_FIND_CHAR_1 = '02....140010000400090702000203004b2a04001205004d2a'
        self.RECV_GATT_FIND_CHAR_2 = '02....0b000700040008((05)|(06))00..000328'
        self.RSP_GATT_FIND_CHAR_2 = '02....140010000400090708001209004d2a0c00020d004a2a'
        self.RECV_GATT_FIND_CHAR_3 = '02....0b000700040008((0d)|(0e))00..000328'
        self.RSP_GATT_FIND_CHAR_3 = '02....0d000900040009070e00040f004c2a'
        self.RECV_GATT_FIND_CHAR_4 = '02....0b0007000400080f00..000328'  # adapt android
        self.RSP_GATT_FIND_CHAR_4 = '02....09000500040001080e000a'
        self.RECV_GATT_FIND_INFO_1 = '02....0900050004000406000700'
        self.RSP_GATT_FIND_INFO_1 = '02....0e000a00040005010600082907000229'
        self.RECV_GATT_FIND_INFO_2 = '02....090005000400040a000b00'
        self.RSP_GATT_FIND_INFO_2 = '02....0e000a00040005010a0008290b000229'
        self.RECV_GATT_FIND_INFO_3 = '02....090005000400040b000c00'
        self.RSP_GATT_FIND_INFO_3 = '02....0e000a00040005010b0008290c000229'
        self.RECV_GATT_FIND_INFO_4 = '02....090005000400040f000f00'
        self.RSP_GATT_FIND_INFO_4 = '02....0a000600040005010f000229'
        self.RECV_GATT_READ_REPORT_MAP = '02....0700030004000a0300'
        self.RSP_GATT_READ_REPORT_MAP = '02....1b00170004000b'
        self.RECV_GATT_READ_REPORT_MAP_CTN = '02....0900050004000c0300..00'
        self.RSP_GATT_READ_REPORT_DATA = '05010906a101850175019508050719e029e715002501' \
                                         '81029501750881039505750105081901290591029501' \
                                         '7503910395067508150026ff000507190029ff8100c0' \
                                         '050c0901a1018502150025017501950d0a240209400a' \
                                         '23020aae010a210209b609cd09b509e209ea09e90930' \
                                         '09408102950175038103c0'
        self.report_data_offset = 0
        self.RSP_GATT_READ_REPORT_MAP_HEADER = '02....1b00170004000d'


        self.RECV_GATT_READ_REPORT_REF1 = '02....0700030004000a0600'
        self.RSP_GATT_READ_REPORT_REF1 = '02....0700030004000b0001'
        self.RECV_GATT_READ_REPORT_REF2 = '02....0700030004000a0a00'
        self.RSP_GATT_READ_REPORT_REF2 = '02....0700030004000b0101'
        self.RECV_GATT_READ_REPORT_INFO = '02....0700030004000a0d00'
        self.RSP_GATT_READ_REPORT_INFO = '02....0900050004000b01020003'
        self.RECV_GATT_WRITE_DES1 = '02....0900050004001207000100'
        self.RSP_GATT_WRITE_DES1_INSUFF = '0208200900050004000108080005'
        self.RSP_GATT_WRITE_DES1 = '02....05000100040013'
        self.RECV_GATT_WRITE_DES2 = '02....090005000400120b000100'
        self.RSP_GATT_WRITE_DES2 = '02....05000100040013'
        self.SEND_GATT_KEY_TEST1 = '02....0f000b0004001B09000000250000000000'
        self.SEND_GATT_KEY_TEST2 = '02....0f000b0004001B09000000000000000000'

class Hid:
    def __init__(self, param):
        self.env = param
        self.bt = BtUsb(self.bt_cb, self.env, rec_log=True, dump_log=True)

    @staticmethod
    def to_string(data):
        return ''.join('{:02x}'.format(x) for x in data)

    def send(self, data):
        return self.bt.send(bytes.fromhex(data))

    def bt_cb(self, data, e):
        if bt_cmp(data, e.CMP_CMP_RESET):
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
        elif bt_cmp(data, e.RECV_LTK_REQ):
            self.env.smp_remote_rand_ediv = self.to_string(data[6:])
            self.env.local_stk = self.to_string(
                brev(btc_s1(b'\x00'*16,
                            brev(bytes.fromhex(self.env.smp_local_rnd)),
                            brev(bytes.fromhex(self.env.smp_remote_rnd)))))
            self.send(e.RSP_RECV_LTK[:4*2]+self.env.handle+self.env.local_stk)
        elif bt_cmp(data, e.RECV_ENC_CHANGE):
            self.send('02'+self.env.handle+e.SEND_ENC_INFO[3*2:-16*2]+self.env.local_ltk)
            self.send('02'+self.env.handle+e.SEND_MASTER_ID[3*2:-10*2]+self.env.smp_local_rand_ediv)
            self.send('02'+self.env.handle+e.SEND_ID_INFO[3*2:-16*2]+self.env.local_irk)
            self.send('02'+self.env.handle+e.SEND_ID_ADDR_INFO[3*2:-7*2]+'00'+self.env.rand_addr)
        elif bt_cmp(data, e.RECV_ENC_INFO):
            self.env.smp_remote_remote_ltk = data[-16*2:]
        elif bt_cmp(data, e.RECV_MASTER_ID):
            self.env.smp_remote_rand_ediv = data[-10*2:]
            self.env.bonded = True
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
        elif bt_cmp(data, e.RECV_GATT_FIND_INFO_3):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_INFO_3[3*2:])
        elif bt_cmp(data, e.RECV_GATT_FIND_INFO_4):
            self.send('02'+self.env.handle+e.RSP_GATT_FIND_INFO_4[3*2:])
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
            if self.env.bonded or True:
                self.send('02'+self.env.handle+e.RSP_GATT_WRITE_DES1[3*2:])
            else:
                self.send('02'+self.env.handle+e.RSP_GATT_WRITE_DES1_INSUFF[3*2:])
        elif bt_cmp(data, e.RECV_GATT_WRITE_DES2):
            self.send('02'+self.env.handle+e.RSP_GATT_WRITE_DES2[3*2:])


    def start(self):
        self.send(self.env.CMD_RESET)

if __name__ == '__main__':
    env = Env()
    hid = Hid(env)
    hid.start()
    import time
    while True:
        time.sleep(5)
        if env.bonded:
            hid.send('02'+env.handle+env.SEND_GATT_KEY_TEST1[3*2:])
            hid.send('02'+env.handle+env.SEND_GATT_KEY_TEST2[3*2:])
