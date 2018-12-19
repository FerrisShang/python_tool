import serial
from threading import Thread, Event
import queue
import time
from struct import pack

__all__ = [
    'BtUart',
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


class BtUart(Event):
    def __init__(self, port, baudrate=115200, rtscts=False, callback=None, param=None, rec_log=True, dump_log=False, rec_path='btsnoop_hci.log'):
        Event.__init__(self)  # use for exit flag
        self.__send_recv_queue__ = queue.Queue()
        self.__callback__ = callback
        self.__param__ = param
        self.__thread_recv__ = None
        self.__thread_proc__ = None
        self.__RX_BUFFER_SIZE__ = 5 * 1024 * 1024  # 5MB
        self.port_name = '{} {} RTSCTS-{}'.format(port, baudrate, 'ON' if rtscts else 'OFF')
        self.__param__ = param
        try:
            self.device = serial.Serial(port=port, baudrate=baudrate, rtscts=rtscts)
            self.device.setTimeout(0.2)
            self.device.setWriteTimeout(0)
            self.device.setBufferSize(self.__RX_BUFFER_SIZE__)
            self.device.flushInput()
            self.device.flushOutput()
        except Exception as e:
            print('Open ' + self.port_name + ' failed:{}\n'.format(e))
            self.device = None
            return
        assert(callback is not None)
        if self.__callback__ is not None:
            self.__thread_recv__ = Thread(target=self.__process__)
            self.__thread_recv__.start()
            self.__thread_proc__ = Thread(target=self.__receive__)
            self.__thread_proc__.start()

        self.rec_log = rec_log
        self.dump_log = dump_log
        if self.rec_log:
            self.__btsnoop__ = BtSnoop(rec_path)

    class Msg:
        TYPE_SEND = 0
        TYPE_RECV = 1

        def __init__(self, msg_type, msg):
            assert(isinstance(msg, bytes))
            self.type = msg_type
            self.data = msg

    def close(self):
        self.set()
        if self.__thread_recv__ is not None:
            self.__thread_recv__.join()
        if self.__thread_proc__ is not None:
            self.__thread_proc__.join()
        if self.device:
            self.device.flush()
            self.device.close()
            self.device = None

    class Closed(Exception):
        pass

    def __process__(self):
        while True:
            try:
                msg = self.__send_recv_queue__.get(timeout=0.2)
                if self.is_set():
                    return
                assert(isinstance(msg, BtUart.Msg))
                if msg.type == msg.type == BtUart.Msg.TYPE_SEND:
                    self.device.write(msg.data)
                elif msg.type == BtUart.Msg.TYPE_RECV:
                    self.__callback__(msg.data, self.__param__)
                if self.rec_log:
                    self.__btsnoop__.record(msg.data, BtSnoop.SEND if msg.type == BtUart.Msg.TYPE_SEND else BtSnoop.RECV)
                if self.dump_log:
                    print(('<<< ' if msg.type <= BtUart.Msg.TYPE_SEND else '>>> ') + ''.join('{:02X} '.format(x) for x in msg.data))
            except queue.Empty:
                if self.is_set():
                    return

    def send(self, data):
        if self.device is not None:
            self.__send_recv_queue__.put(BtUart.Msg(BtUart.Msg.TYPE_SEND, data))

    def recv(self, length, flag=False):
        res = b''
        cnt = length
        while True:
            try:
                if self.is_set():
                    raise self.Closed
                if cnt == 0:
                    return res
                data = self.device.read(cnt)
                res += data
                cnt -= len(data)
                if flag:
                    return res
            except IOError:
                print('Uart IO error')
                raise

    def __receive__(self):
        while True:
            try:
                stream = b''
                head = self.recv(1)
                stream += head
                length = 0
                if int.from_bytes(head, 'little') == 0x01:
                    op_length = self.recv(3)
                    stream += op_length
                    length = int.from_bytes(op_length[-1:], 'little')
                elif int.from_bytes(head, 'little') == 0x02:
                    handle_length = self.recv(4)
                    stream += handle_length
                    length = int.from_bytes(handle_length[-2:], 'little')
                elif int.from_bytes(head, 'little') == 0x04:
                    evt_length = self.recv(2)
                    stream += evt_length
                    length = int.from_bytes(evt_length[-1:], 'little')
                elif int.from_bytes(head, 'little') == 0x05:
                    head_length = self.recv(8)
                    stream += head_length
                    length = int.from_bytes(head_length[-2:], 'little')
                data = self.recv(length, True)
                stream += data
                if stream != '':
                    self.__send_recv_queue__.put(BtUart.Msg(BtUart.Msg.TYPE_RECV, stream))
            except self.Closed:
                return
            except Exception as e:
                print('Uart device error: {}'.format(str(e)))
                raise


def __recv_cb__(msg, param):
    print(msg, param)


if __name__ == '__main__':
    bt_uart = BtUart('COM1', baudrate=115200, rtscts=True, callback=__recv_cb__, dump_log=True)
    bt_uart.send(b'\x01\x03\x0c\x00')
    from time import sleep
    sleep(10)
    bt_uart.close()
