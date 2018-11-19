# https://github.com/pyusb
import usb
import threading
import queue
import os
import time
from struct import pack


__all__ = [
    'BtUsb',
]


class BtSnoop:
    BT_SNOOP_HEADER = b'btsnoop\x00\x00\x00\x00\x01\x00\x00\x03\xEA'
    BT_SNOOP_RECORD_FMT = '>IIIIQ%ds'
    SEND = 0
    RECV = 1

    def __init__(self, file_name='btsnoop_hci.log'):
        self.f = open(file_name, 'wb')
        self.f.write(BtSnoop.BT_SNOOP_HEADER)

    def record(self, bt_stream, direction):
        length = len(bt_stream)
        timestamp = int(time.time() * 1000000) + 0x00dcddb30f2f8000
        flag = direction
        if bt_stream[0] == 1 or bt_stream[0] == 4:
            flag |= 0x02
        stream = pack(BtSnoop.BT_SNOOP_RECORD_FMT % (length,), length, length, flag, 0, timestamp, bt_stream)
        self.f.write(stream)
        self.f.flush()


class BtUsb:
    def __init__(self, callback=None, param=None, id_vendor=0x0a5c, id_product=0x21ec, rec_log=True, dump_log=False, rec_path='btsnoop_hci.log'):
        self.__INT_R_ENDP__ = 0x81
        self.__CMD_W_ENDP__ = 0
        self.__ACL_R_ENDP__ = 0x82
        self.__ACL_W_ENDP__ = 2
        self.__send_recv_queue__ = queue.Queue()
        self.__callback__ = callback
        self.__param__ = param
        self.__dev__ = usb.core.find(idVendor=id_vendor, idProduct=id_product)
        if self.__dev__ is None:
            print('Device not found!')
            return
        assert(callback is not None)
        assert(isinstance(self.__dev__, usb.core.Device))
        try:
            self.__dev__.detach_kernel_driver(0)
        except:
            pass
        self.__dev__.set_configuration(1)
        self.__dev__.set_interface_altsetting(interface=0, alternate_setting=0)
        self.__dev__.set_interface_altsetting(interface=1, alternate_setting=0)

        if self.__callback__ is not None:
            threading.Thread(target=self.__process__).start()
            threading.Thread(target=self.__recv_evt__).start()
            threading.Thread(target=self.__recv_acl__).start()

        self.rec_log = rec_log
        self.dump_log = dump_log
        if self.rec_log:
            self.__btsnoop__ = BtSnoop(rec_path)

    class Msg:
        TYPE_CMD = 0
        TYPE_SEND_ACL = 1
        TYPE_RECV_ACL = 2
        TYPE_EVT = 3

        def __init__(self, msg_type, msg):
            assert(isinstance(msg, bytes))
            self.type = msg_type
            self.data = msg

    def __process__(self):
        while True:
            msg = self.__send_recv_queue__.get()
            assert(isinstance(msg, BtUsb.Msg))
            if msg.type == BtUsb.Msg.TYPE_CMD:
                self.__dev__.ctrl_transfer(32, 0, 0, 0, msg.data[1:], timeout=4096)
            elif msg.type == BtUsb.Msg.TYPE_SEND_ACL:
                self.__dev__.write(self.__ACL_W_ENDP__, msg.data[1:], timeout=4096)
            elif msg.type == BtUsb.Msg.TYPE_RECV_ACL:
                self.__callback__(msg.data, self.__param__)
            elif msg.type == BtUsb.Msg.TYPE_EVT:
                self.__callback__(msg.data, self.__param__)
            if self.rec_log:
                self.__btsnoop__.record(msg.data, BtSnoop.SEND if msg.type <= BtUsb.Msg.TYPE_SEND_ACL else BtSnoop.RECV)
            if self.dump_log:
                print(('<<< ' if msg.type <= BtUsb.Msg.TYPE_SEND_ACL else '>>> ') + ''.join('{:02X} '.format(x) for x in msg.data))

    def send(self, data):
        if data[0] == 0x01:
            self.__send_recv_queue__.put(BtUsb.Msg(BtUsb.Msg.TYPE_CMD, data))
        else:
            self.__send_recv_queue__.put(BtUsb.Msg(BtUsb.Msg.TYPE_SEND_ACL, data))

    def __recv_evt__(self):
        while True:
            try:
                pkt = self.__dev__.read(self.__INT_R_ENDP__, 4096, timeout=-1)
                if pkt != '':
                    self.__send_recv_queue__.put(BtUsb.Msg(BtUsb.Msg.TYPE_EVT, b'\x04' + pkt))
            except usb.core.USBError as e:
                print('USB device error: {}'.format(str(e)))
                os._exit(0)

    def __recv_acl__(self):
        while True:
            try:
                pkt = self.__dev__.read(self.__ACL_R_ENDP__, 4096, timeout=-1)
                if pkt != '':
                    self.__send_recv_queue__.put(BtUsb.Msg(BtUsb.Msg.TYPE_RECV_ACL, b'\x02' + pkt))
            except usb.core.USBError:
                pass


def __recv_cb__(msg, param):
    print(msg)

if __name__ == '__main__':
    bt_usb = BtUsb(__recv_cb__, dump_log=True)
    bt_usb.send(b'\x01\x03\x0c\x00')
