import serial
from threading import Thread, Event
import queue
import time

__all__ = [
    'GsmUart',
]


class GsmLog:
    SEND = 1
    RECV = 0

    def __init__(self, file_name):
        self.f = open(file_name, 'w')

    def record(self, stream, direction):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.f.write(timestamp + (' OUT: ' if direction == self.SEND else '  IN: ') + stream + '\n')
        self.f.flush()


class GsmUart(Event):
    DIR_RECV = 0
    DIR_SEND = 1

    def __init__(self, port, baudrate=115200, rtscts=False, callback=None, param=None, dump_log=True, rec_log=True, rec_path='gsm.log'):
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
            self.device.timeout = 0.2
            if hasattr(self.device, 'setBufferSize'):
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
            self.__gsm_log__ = GsmLog(rec_path)

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
                direction, data = self.__send_recv_queue__.get(timeout=0.2)
                assert(isinstance(data, bytes))
                if self.is_set():
                    return
                try:
                    data_str = data.decode('utf-8').strip()
                except UnicodeDecodeError:
                    data_str = str(data)
                if direction == self.DIR_RECV:
                    if self.__callback__ and len(data_str) > 0:
                        self.__callback__(data_str, self.__param__)
                elif direction == self.DIR_SEND:
                    self.device.write(data)
                if self.rec_log and len(data_str) > 0:
                    self.__gsm_log__.record(data_str, direction)
                if self.dump_log and len(data_str) > 0:
                    print(('<<< ' if direction == self.DIR_SEND else '>>> ') + data_str)
            except queue.Empty:
                if self.is_set():
                    return

    def send(self, data):
        if self.device is not None:
            if isinstance(data, bytes):
                self.__send_recv_queue__.put((self.DIR_SEND, data))
            elif isinstance(data, str):
                data = bytes(data.strip() + '\r\n', encoding='utf-8')
                self.__send_recv_queue__.put((self.DIR_SEND, data))

    def recv(self):
        stream = b''
        while True:
            try:
                if self.is_set():
                    raise self.Closed
                assert(isinstance(self.device, serial.Serial))
                data = self.device.read(1)
                if data == b'\n':
                    if len(str(stream).strip()) == 0:
                        return ''
                    else:
                        return stream
                stream += data
            except IOError:
                print('Uart IO error')
                raise

    def __receive__(self):
        while True:
            try:
                stream = self.recv()
                if len(stream) > 0:
                    self.__send_recv_queue__.put((self.DIR_RECV, stream))
            except self.Closed:
                return
            except Exception as e:
                print('Uart device error: {}'.format(str(e)))
                raise


def __recv_cb__(msg, param):
    pass


if __name__ == '__main__':
    bt_uart = GsmUart('/dev/ttyUSB1', baudrate=115200, rtscts=False, callback=__recv_cb__, dump_log=True)
    bt_uart.send(bytes('AT\r\n', encoding='utf-8'))
    bt_uart.send('ATE1')
    time.sleep(3)
    bt_uart.close()
