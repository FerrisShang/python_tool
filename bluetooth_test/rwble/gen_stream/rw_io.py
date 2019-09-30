from threading import Thread, Event
import struct
import serial
import queue


__all__ = [
    'RwAhiIO'
]


class SerialPort:
    def __init__(self, port, baudrate=115200, rtscts=False):
        self._RX_BUFFER_SIZE = 5 * 1024 * 1024  # 5MB
        self.prot_name = '{} {} RTSCTS-{}'.format(port, baudrate, 'ON' if rtscts else 'OFF')
        self.device = None
        try:
            self.device = serial.Serial(port=port, baudrate=baudrate, rtscts=rtscts)
            self.device.flushInput()
            self.device.flushOutput()
            if hasattr(self.device, 'setBufferSize'):
                self.device.setBufferSize(self._RX_BUFFER_SIZE)
        except Exception as e:
            print('Open ' + self.prot_name + ' failed\n')
            raise

    def __write__(self, stream):
        return self.device.write(stream)

    def __read__(self, size):
        return self.device.read(size)

    def __del__(self):
        if self.device:
            self.device.flush()
            self.device.close()

_ST_AHI_GET_HEADER  = 1
_ST_AHI_GET_DATA    = 2
_ST_AHI_FINISH      = 3
_ST_AHI_ERROR       = 4
_ST_AHI_IO_CLOSE    = 5


class RwAhiIO:
    def __init__(self, port, baudrate=115200, rtscts=False):
        self.exit_flag = Event()
        self.dev = SerialPort(port, baudrate, rtscts)
        self.read_thread = Thread(target=self.__read_data)
        self.packages = queue.Queue()
        self.read_thread.start()

    def close(self):
        self.exit_flag.set()
        self.dev.device.close()
        self.dev.device = None
        self.read_thread.join(1)

    def recv(self, timeout=None):
        try:
            r = self.packages.get(timeout=timeout)
        except:
            r = None
        return r

    def peek(self):
        if self.packages.empty():
            return None
        else:
            with self.packages.mutex:
                return self.packages.queue[0]

    def clear(self):
        with self.packages.mutex:
            self.packages.queue.clear()

    def send(self, stream):
        self.dev.__write__(stream)

    def __get_stream(self, stream=b'', status=_ST_AHI_GET_HEADER):
        if status == _ST_AHI_GET_HEADER:
            recv_length = 9
            status = _ST_AHI_GET_DATA
        elif status == _ST_AHI_GET_DATA:
            if not (stream[0] == b'\x05'[0]):
                return _ST_AHI_ERROR, None
            recv_length = struct.unpack('<H', stream[-2:])[0]
            status = _ST_AHI_FINISH
        elif status == _ST_AHI_FINISH:
            return status, stream
        else:
            return _ST_AHI_ERROR, None
        if recv_length == 0:
            return status, stream
        recv = self.dev.__read__(recv_length)
        if len(recv) != recv_length:
            if self.exit_flag.is_set():
                return _ST_AHI_IO_CLOSE, None
            else:
                return _ST_AHI_ERROR, None
        stream += recv
        return self.__get_stream(stream, status)

    def __read_data(self):
        while True:
            try:
                (status, stream) = self.__get_stream()
                if status == _ST_AHI_ERROR:
                    raise Exception('BT read package error')
                elif status == _ST_AHI_FINISH:
                    self.packages.put(stream)
            except IOError as e:
                print(self.dev.prot_name + ' read error')
                break
            except Exception as e:
                if self.exit_flag.is_set():
                    break
                print(e)
                from time import sleep
                sleep(0.05)
                self.dev.device.flushInput()

if __name__ == '__main__':
    bt_port = RwAhiIO('COM9', 230400)
    stream = b'\x05\x02\x0d\x0d\x00\x10\x00\x01\x00\x01'
    bt_port.send(stream)
    r = bt_port.recv()
    print(' '.join(['%02x' % ord(c) for c in r]))
    bt_port.close()