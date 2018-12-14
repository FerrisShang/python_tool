from bt_usb import *
from random import randint
from threading import Timer


class Item:
    TYPE_VARIABLE = 0
    TYPE_PLACEHOLDER = 1
    TYPE_HEX_DATA = 2

    def __init__(self, item_type, name='', data=b'', length=0):
        self.data = data
        self.name = name
        self.length = length
        self.type = item_type

    def __str__(self):
        return 'Item: T-{} L-{} N-{} D-{}'.format(self.type, self.length, self.name, self.data)


class LineParam:
    def __init__(self, variable_pool, str_line):
        assert(isinstance(variable_pool, dict))
        assert(isinstance(str_line, str))
        self.var_pool = variable_pool
        self.title = ''
        self.repeat = 1
        self.delay = 0
        self.item_list = []
        if '#' == str_line.strip()[0] or ':' not in str_line:
            return
        data_str = str_line.split(':')
        assert(len(data_str) == 2)
        self.title = data_str[0].strip()
        tmp = self.title.split()
        if len(tmp) == 2:
            self.title, self.repeat = tmp[0].strip(), int(tmp[1].strip())
        elif len(tmp) == 3:
            self.title, self.repeat, self.delay = tmp[0].strip(), int(tmp[1].strip()), int(tmp[2].strip())
        data_str = data_str[1].strip()
        pos = 0
        while pos < len(data_str):
            idx_st = data_str.find('{', pos)
            if idx_st >= 0:
                if idx_st > 0:
                    item = Item(Item.TYPE_HEX_DATA, data=bytes.fromhex(data_str[pos:].split('{')[0]))
                    if len(item.data) > 0:
                        self.item_list.append(item)
                idx_ed = data_str.find('}', pos)
                assert(idx_ed - idx_st > 1)
                str_var = data_str[idx_st+1:idx_ed]
                if ',' in str_var:
                    tmp = str_var.split(',')
                    item = Item(Item.TYPE_PLACEHOLDER, name=tmp[0].strip(), length=int(tmp[1].strip()))
                else:
                    item = Item(Item.TYPE_VARIABLE, name=str_var.strip())
                self.item_list.append(item)
                pos = idx_ed+1
            else:
                item = Item(Item.TYPE_HEX_DATA, data=bytes.fromhex(data_str[pos:]))
                self.item_list.append(item)
                break

    def to_hex(self):
        res = b''
        for item in self.item_list:
            if item.type == Item.TYPE_VARIABLE:
                if item.name not in self.var_pool:
                    print('Variable not in pool!')
                    assert False
                res += self.var_pool[item.name]
            elif item.type == Item.TYPE_PLACEHOLDER:
                res += bytes([randint(0, 0xFF) for _ in range(item.length)])
            elif item.type == Item.TYPE_HEX_DATA:
                res += item.data
        return res

    def hexcmp(self, cmp_data):
        assert(isinstance(cmp_data, bytes))
        pos = 0
        tmp_var_pool = {}
        for item in self.item_list:
            if item.type == Item.TYPE_VARIABLE:
                if item.name in self.var_pool:
                    var_data = self.var_pool[item.name]
                    if pos + len(var_data) <= len(cmp_data) and var_data == cmp_data[pos:pos+len(var_data)]:
                        pos += len(var_data)
                    else:
                        return False
                else:
                    return False
            elif item.type == Item.TYPE_PLACEHOLDER:
                if item.length == 0:
                    tmp_var_pool[item.name] = cmp_data[pos:]
                    pos += len(cmp_data[pos:])
                elif pos + item.length <= len(cmp_data):
                    tmp_var_pool[item.name] = cmp_data[pos:pos + item.length]
                    pos += item.length
                else:
                    return False
            elif item.type == Item.TYPE_HEX_DATA:
                if pos + len(item.data) <= len(cmp_data) and item.data == cmp_data[pos:pos+len(item.data)]:
                    pos += len(item.data)
                else:
                    return False
        if pos == len(cmp_data):
            for n, d in tmp_var_pool.items():
                self.var_pool[n] = d
            return True
        else:
            return False

    def dump(self):
        pass


class SnoopRepeat:
    class SrPair:
        def __init__(self, send=None, recv=None, recv_cnt=0):
            self.send = send
            self.recv = recv
            self.recv_cnt = recv_cnt

    def __init__(self):
        self.variable_pool = {}
        self.line_list = []
        self.sr_list = []
        self.__cur_sr__ = SnoopRepeat.SrPair(recv=LineParam(self.variable_pool, 'RECV:040E0401030C00'))

    def parse_line(self, line_str):
        assert(isinstance(line_str, str))
        if line_str.strip()[0] == '#':
            return
        lp = LineParam(self.variable_pool, line_str)
        self.line_list.append(lp)
        if lp.title == 'SEND':
            self.__cur_sr__.send = lp
            self.sr_list.append(self.__cur_sr__)
            self.__cur_sr__ = SnoopRepeat.SrPair()
        elif lp.title == 'RECV':
            self.__cur_sr__.recv = lp

    def parse_file(self, path):
        f = open(path, 'r')
        for line in f.readlines():
            self.parse_line(line)
        f.close()

    def get_response(self, cmp_data):
        for sr in self.sr_list:
            assert(isinstance(sr, SnoopRepeat.SrPair))
            assert(isinstance(sr.recv, LineParam))
            if sr.recv.hexcmp(cmp_data):
                sr.recv_cnt += 1
                if sr.recv_cnt >= sr.recv.repeat:
                    sr.recv_cnt = 0
                    return sr
        return None

    def var_add(self, name, data):
        self.variable_pool[name] = data

    def dump_var(self):
        for name, data in self.variable_pool.items():
            print('{}: {}'.format(name, ''.join('{:02X} '.format(x) for x in data)))


def bt_usb_callback(data, param):
    if not hasattr(bt_usb_callback, "last_sr"):
        bt_usb_callback.last_sr = None
    sr = param
    assert(isinstance(sr, SnoopRepeat))
    rsp = sr.get_response(data)
    if rsp is not None and bt_usb_callback.last_sr != rsp:
        assert(isinstance(rsp.send, LineParam))
        bt_usb_callback.last_sr = rsp
        rsp_data = rsp.send.to_hex()
        for _ in range(rsp.send.repeat):
            if rsp.send.delay > 0:
                Timer((rsp.send.delay + randint(-10, 10)) / 1000, bt_usb.send, [rsp_data]).start()
            else:
                bt_usb.send(rsp_data)

if __name__ == '__main__':
    _sr = SnoopRepeat()
    _sr.parse_file('snoop_rec.txt')
    bt_usb = BtUsb(bt_usb_callback, _sr, dump_log=True)
    bt_usb.send(b'\x01\x03\x0c\x00')
