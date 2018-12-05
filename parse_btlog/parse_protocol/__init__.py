import xlrd
from collections import OrderedDict
from itertools import chain
from enum import Enum
from struct import pack, unpack


__all__ = [
    'UnpackStream',
]


class ProtoFormat:
    class Item:
        def __init__(self, remark, parameters):
            self.remark = str(remark).strip()
            self.parameters = str(parameters).strip()

    def __init__(self, command, remark, key_code, parameters):
        assert(isinstance(command, str) and isinstance(parameters, str))
        if type(key_code) is str:
            key_code = int(key_code, 0)
        self.command = command.strip()
        self.fmt_list = OrderedDict()
        if key_code != '':
            self.fmt_list[key_code] = self.Item(remark, parameters)

    def add(self, remark, key_code, parameters):
        if key_code != '':
            if type(key_code) is str:
                key_code = int(key_code, 0)
            if key_code in self.fmt_list:
                print('Warning: key_code conflict:', key_code)
            else:
                self.fmt_list[key_code] = self.Item(remark, parameters)
        else:
            print('Warning: key_code is empty.')

    def dump(self):
        print(self.command)
        for k, item in self.fmt_list.items():
            print('    0x{:04x}  {} {}'.format(
                k, item.remark + (' '*(60-len(item.remark)) if len(item.remark) < 60 else ''), item.parameters))


class ProtoParam:
    class Item:
        def __init__(self, value_or_range, description):
            self.value_or_range = value_or_range
            self.description = description

    def __init__(self, name, bit_width, data_type, key, value_or_range, default, sub_key, description):
        assert name != ''
        self.name = name
        self.bit_width = bit_width
        self.data_type = data_type
        self.key = key
        self.value_or_range = value_or_range
        self.default = default
        self.sub_key = sub_key
        self.description = description
        self.param_list = OrderedDict()
        try:
            if data_type == 'enum':
                self.param_list[key] = self.Item(value_or_range, description)
        except AttributeError:
            pass

    def dump(self):
        if self.data_type != 'enum':
            print('{:30s}  {:10s} {}  {}'.format(self.name, self.data_type, self.bit_width, self.sub_key))
        else:
            print('{:30s}  {:10s} {}'.format(self.name, self.data_type, self.bit_width))
            for k, item in self.param_list.items():
                print('    {:60s}  {}'.format(k, item.value_or_range))

    def add(self, key, value_or_range, description):
        if key != '':
            self.param_list[key] = self.Item(value_or_range, description)
        else:
            print('Warning: key is empty.')


class ProtoParse:
    RESERVED_LINE = 1
    FMT_IDX_CMD = 0
    FMT_IDX_REMARK_CMD = 1
    FMT_IDX_KEY_CODE_CMD = 2
    FMT_IDX_PARAMS_CMD = 3
    FMT_IDX_MAX = 4
    PARAM_IDX_NAME = 0
    PARAM_IDX_BIT_WIDTH = 1
    PARAM_IDX_TYPE = 2
    PARAM_IDX_KEY = 3
    PARAM_IDX_VALUE_RANGE = 4
    PARAM_IDX_DEFAULT = 5
    PARAM_IDX_SUB_KEY = 6
    PARAM_IDX_DESCRIPTION = 7
    PARAM_IDX_MAX = 8

    def __init__(self, filename='parse_protocol/parse.xlsx', sheet_format_name='Format', sheet_param_name='Param'):
        book = xlrd.open_workbook(filename)
        sheet_format = book.sheet_by_name(sheet_format_name)
        sheet_param = book.sheet_by_name(sheet_param_name)
        format_data_list = [sheet_format.row_values(i) for i in range(ProtoParse.RESERVED_LINE, sheet_format.nrows)]
        format_data_list = [[int(a) if type(a) == float else str(a).strip() for a in j] for j in format_data_list]
        param_data_list = [sheet_param.row_values(i) for i in range(ProtoParse.RESERVED_LINE, sheet_param.nrows)]
        param_data_list = [[int(a) if type(a) == float else str(a).strip() for a in j] for j in param_data_list]
        last_fmt_item = None
        last_param_item = None
        self.fmt_list = OrderedDict()
        self.param_list = OrderedDict()
        # Format Data
        for i in range(len(format_data_list)):
            fmt = format_data_list[i]
            if fmt[self.FMT_IDX_CMD] != '' and fmt[self.FMT_IDX_KEY_CODE_CMD] != '':
                hci_format = ProtoFormat(*fmt[:self.FMT_IDX_MAX])
                self.fmt_list[fmt[self.FMT_IDX_CMD]] = hci_format
                last_fmt_item = hci_format
            elif fmt[self.FMT_IDX_CMD] == '' and fmt[self.FMT_IDX_KEY_CODE_CMD] != '' and last_fmt_item is not None:
                assert(isinstance(last_fmt_item, ProtoFormat))
                last_fmt_item.add(*fmt[self.FMT_IDX_REMARK_CMD:self.FMT_IDX_MAX])
            else:
                print('Data format parse error: line{} in "{}"'.format(i+1, sheet_param))
        # Parameters Data
        for i in range(len(param_data_list)):
            param = param_data_list[i]
            if param[self.PARAM_IDX_NAME] != '' and param[self.PARAM_IDX_BIT_WIDTH] != '' and \
                    param[self.PARAM_IDX_TYPE] != '':
                hci_format = ProtoParam(*param[:self.PARAM_IDX_MAX])
                if param[self.PARAM_IDX_NAME].strip() in self.param_list:
                    print('Error, Param {} redefined !'.format(param[self.PARAM_IDX_NAME].strip()))
                self.param_list[param[self.PARAM_IDX_NAME].strip()] = hci_format
                last_param_item = hci_format
            elif param[self.PARAM_IDX_NAME] == '' and param[self.PARAM_IDX_BIT_WIDTH] == '' and \
                    param[self.PARAM_IDX_TYPE] == '' and param[self.PARAM_IDX_KEY] != '' and \
                    param[self.PARAM_IDX_VALUE_RANGE] != '':  # enum
                assert(isinstance(last_param_item, ProtoParam))
                last_param_item.add(
                    param[self.PARAM_IDX_KEY], param[self.PARAM_IDX_VALUE_RANGE], param[self.PARAM_IDX_DESCRIPTION])
            else:
                print('Data parameter parse error: line{} in <{}> <{}>'.
                      format(i+1, sheet_param_name, repr(param[self.PARAM_IDX_NAME])))
        self.check()

    def check(self):
        list_param_in_fmt = [k for k, v in self.fmt_list.items()]
        list_param_all_in_fmt = [[x.parameters for _, x in hf.fmt_list.items()] for _, hf in self.fmt_list.items()]
        list_param_all_in_fmt = list(chain.from_iterable(list_param_all_in_fmt))
        list_param_all_in_fmt = [s.split(',') for s in list_param_all_in_fmt]
        list_param_all_in_fmt = list(chain.from_iterable(list_param_all_in_fmt))
        list_params = [x for x, v in self.param_list.items()]
        error_undef = set(list_param_all_in_fmt + list_param_in_fmt) - set(list_params)
        if len(error_undef) > 0:
            print('Error: undefined parameters - {}'.format(error_undef))
        warning_def = set(list_params) - set(list_param_all_in_fmt + list_param_in_fmt)
        if len(warning_def) > 0:
            print('Warning: unused parameters - {}'.format(warning_def))
        for p in list_param_in_fmt:
            if p in self.param_list and self.param_list[p].sub_key == '':
                print('Error: parameter {} missing the sub_key'.format(p))
        for k, v in self.param_list.items():
            if v.sub_key != '' and k not in self.fmt_list:
                print('Error: parameter "{}" missing the parse format'.format(k))

    def dump(self):
        for v, k in self.fmt_list.items():
            k.dump()
        for v, k in self.param_list.items():
            k.dump()

    def to_code(self):
        code_lines = ''
        code_lines += 'from enum import Enum\n\n\n'
        for name, param in self.param_list.items():  # parameters
            assert(isinstance(param, ProtoParam))
            code_lines += 'class {}{}:\n'.format(param.name, '' if param.data_type != 'enum' else '(Enum)')
            if isinstance(param.bit_width, str):
                if '/' in param.bit_width:
                    code_lines += '    __bit_width__ = {}\n'.format(repr(param.bit_width))
                else:
                    code_lines += '    __bit_width__ = {}\n'.format(int(param.bit_width, 0))
            else:
                code_lines += '    __bit_width__ = {}\n'.format(param.bit_width)
            code_lines += '    __data_type__ = {}\n'.format(repr(param.data_type))
            if len(param.default) > 0:
                code_lines += '    __default__ = {}\n'.format(param.default)
            if param.data_type != 'enum':
                if len(param.value_or_range) > 0:
                    code_lines += '    __range__ = {}\n'.format(repr(param.value_or_range))
                if len(param.sub_key) > 0:
                    code_lines += '    __sub_key__ = {}\n'.format(repr(param.sub_key))
                if len(param.description) != 0:
                    code_lines += '    __description__ = {}\n'.format(repr(param.description))
            else:
                for k, v in param.param_list.items():
                    code_lines += '    {} = {}\n'.format(k, v.value_or_range)
                    if len(v.description) != 0:
                        code_lines += '    __Des_{}__ = {}\n'.format(k, repr(v.description))
            code_lines += '\n\n'
        for name, fmt in self.fmt_list.items():  # formats
            assert(isinstance(fmt, ProtoFormat))
            code_lines += 'fmt_{}'.format(fmt.command) + ' = {\n'
            sub_key = self.param_list[fmt.command].sub_key
            for k, v in self.param_list[sub_key].param_list.items():
                code_lines += '    {}: [{}],\n'.format(
                    '{}.{}'.format(sub_key, k),
                    fmt.fmt_list[int(v.value_or_range, 0)].parameters.replace(' ', '').replace(',', ', '))
            code_lines += '}\n'
        return code_lines

    def to_file(self, filename='param.py'):
        code_lines = self.to_code()
        with open(filename, 'w') as f:
            f.write(code_lines)
            f.close()
        return code_lines

exec(ProtoParse().to_file())


class UnpackStream:
    class Item:
        def __init__(self, p_class, p_value, p_sub=None, success=True):
            self.p_class = p_class
            self.p_value = p_value
            self.p_sub = p_sub
            self.bit_cnt = 0
            self.success = success

    class OutType(Enum):
        u8 = 0  # E.g. 1
        s8 = 1  # E.g. -1
        u16 = 2  # E.g. 11111
        s16 = 3  # E.g. -11111
        u32 = 4  # E.g. 11111111
        s32 = 5  # E.g. -11111111
        u64 = 6  # E.g. 11111111111111
        s64 = 7  # E.g. -11111111111111
        s = 8  # E.g. 12 34 ab cd
        S = 9  # E.g. 12 34 AB CD
        x = 10  # E.g. 0x123abc
        X = 11  # E.g. 0x123ABC
        bit = 12  # E.g. 00010000: MASK_INPUT
        DD = 13  # E.g. AA:BB:DD:CC:EE:FF
        T0_625ms = 14  # E.g. 0x01: 0.624ms
        T1_25ms = 15  # E.g. 0x01: 2.5ms
        T10ms = 16  # E.g. 0x02: 20ms
        enum = 17  # E.g. 0: SUCCESS

    class ParseError(Exception):
        pass

    @staticmethod
    def param2str(param):
        assert(isinstance(param, UnpackStream.Item))
        if not param.success:
            data_str = ''.join('{:02X} '.format(x) for x in param.p_value)
        else:
            try:
                p_type = param.p_class.__data_type__
                if p_type == 'u8':
                    data_str = str(unpack('B', param.p_value)[0])
                elif p_type == 's8':
                    data_str = str(unpack('b', param.p_value)[0])
                elif p_type == 'u16':
                    data_str = str(unpack('<H', param.p_value)[0])
                elif p_type == 's16':
                    data_str = str(unpack('<h', param.p_value)[0])
                elif p_type == 'u32':
                    data_str = str(unpack('<I', param.p_value)[0])
                elif p_type == 's32':
                    data_str = str(unpack('<i', param.p_value)[0])
                elif p_type == 'u64':
                    data_str = str(unpack('<Q', param.p_value)[0])
                elif p_type == 's64':
                    data_str = str(unpack('<q', param.p_value)[0])
                elif p_type == 's':
                    data_str = ''.join('{:02x} '.format(x) for x in param.p_value)
                elif p_type == 'S':
                    data_str = ''.join('{:02X} '.format(x) for x in param.p_value)
                elif p_type == 'x':
                    h_byte = ((int(param.p_class.__bit_width__.split('/')[1], 0)+4)//8)*2 if \
                        isinstance(param.p_class.__bit_width__, str) else ((param.p_class.__bit_width__+4)//8)*2
                    data_str = ''.join(('0x{:0%dx}' % h_byte).format(int.from_bytes(param.p_value, 'little')))
                elif p_type == 'X':
                    h_byte = ((int(param.p_class.__bit_width__.split('/')[1], 0)+4)//8)*2 if \
                        isinstance(param.p_class.__bit_width__, str) else ((param.p_class.__bit_width__+4)//8)*2
                    data_str = ''.join(('0x{:0%dX}' % h_byte).format(int.from_bytes(param.p_value, 'little')))
                elif p_type == 'DD':
                    data_str = ':'.join('{:02X}'.format(x) for x in param.p_value[::-1])
                elif p_type == 'T0_625ms':
                    data_str = ''.join('0x{:02X}'.format(int.from_bytes(param.p_value, 'little'))) + \
                           ' (' + str(int.from_bytes(param.p_value, 'little') * 0.625) + 'ms' + ')'
                elif p_type == 'T1_25ms':
                    data_str = ''.join('0x{:02X}'.format(int.from_bytes(param.p_value, 'little'))) + \
                           ' (' + str(int.from_bytes(param.p_value, 'little') * 1.25) + 'ms' + ')'
                elif p_type == 'T10ms':
                    data_str = ''.join('0x{:02X}'.format(int.from_bytes(param.p_value, 'little'))) + \
                           ' (' + str(int.from_bytes(param.p_value, 'little') * 10) + 'ms' + ')'
                elif p_type == 'enum':
                    value, enum_value = int.from_bytes(param.p_value, 'little'), [item.value for item in param.p_class]
                    if value in enum_value and hasattr(param.p_class, '__Des_{}__'.format(param.p_class(value).name)):
                        data_str = eval(param.p_class.__name__+'.__Des_{}__'.format(param.p_class(value).name))
                    else:
                        data_str = str(param.p_class(int.from_bytes(param.p_value, 'little')).name)
                    data_str += ' (' + ''.join('0x{:02X}'.format(int.from_bytes(param.p_value, 'little'))) + ')'
                else:
                    raise ValueError
            except ValueError:
                data_str = ''.join('{:02X} '.format(x) for x in param.p_value) + ' (Unknown)'

        if param.p_class.__data_type__ != 'enum' and hasattr(param.p_class, '__description__'):
            title_str = eval(param.p_class.__name__+'.__description__')
        else:
            title_str = param.p_class.__name__.replace('_', ' ')
        return ' ' * 4 + '{:30s}: {}'.format(title_str, data_str)

    def __init__(self, stream):
        self.result = []
        self.unpack(stream)

    def unpack(self, stream, unpack_fmt=None, key=None, param=None):
        # assert(isinstance(stream, bytes))
        if param is None:
            param = self.result
        if unpack_fmt is None:
            unpack_fmt = eval('fmt_PROTO_ALL')
            key = eval('DEFAULT.KEY')
        len_cnt = 0
        bit_cnt = 0
        try:
            for p_class in unpack_fmt[key]:
                if len_cnt >= len(stream):
                    break
                if isinstance(p_class.__bit_width__, str):
                    assert('/' in p_class.__bit_width__)
                    cnt, bit_all = [int(num, 0) for num in p_class.__bit_width__.split('/')]
                    p_len = bit_all // 8
                    if len_cnt + p_len > len(stream):
                        param.append(self.Item(p_class, stream[len_cnt:], None, False))
                        break
                    else:
                        value_bytes = stream[len_cnt:len_cnt+p_len]
                        value = int.from_bytes(value_bytes, 'little')
                        value = (value >> (bit_all - cnt - bit_cnt)) & ~((-1) << cnt)
                        value_bytes = pack('<' + 'H', value)
                        item = self.Item(p_class, value_bytes)
                        item.bit_cnt = bit_cnt
                        param.append(item)
                        bit_cnt += cnt
                        if bit_cnt >= bit_all:
                            bit_cnt = 0
                            len_cnt += p_len
                else:
                    bit_cnt = 0  # reset bit_cnt
                    if p_class.__bit_width__ > 0:
                        p_len = p_class.__bit_width__ // 8
                    elif p_class.__bit_width__ == 0:
                        p_len = len(stream[len_cnt:])
                    else:
                        p_len = len(stream[len_cnt:p_class.__bit_width__//8])

                    if len_cnt + p_len > len(stream):
                        item = self.Item(p_class, stream[len_cnt:], None, False)
                    elif hasattr(p_class, '__sub_key__'):
                        item = self.Item(p_class, stream[len_cnt:len_cnt+p_len], [])
                    else:
                        item = self.Item(p_class, stream[len_cnt:len_cnt+p_len])
                    len_cnt += p_len
                    param.append(item)
            if len_cnt < len(stream):
                param.append(self.Item(eval('Unused'), stream[len_cnt:]))
            for item in param:
                if item.p_sub is not None:
                    try:
                        if item.p_class.__sub_key__ == 'DEFAULT':
                            sub_key = eval('DEFAULT.KEY')
                        else:
                            sub_key = None
                            for find_k in param:
                                if find_k.p_class.__name__ == item.p_class.__sub_key__:
                                    sub_key = int.from_bytes(find_k.p_value, 'little')
                                    sub_key = find_k.p_class(sub_key)
                                    break
                        item.success = self.unpack(item.p_value, eval('fmt_' + item.p_class.__name__), sub_key, item.p_sub)
                    except ValueError:
                        item.success = False
            return True
        except ValueError:
            if len_cnt < len(stream):
                param.append(self.Item(eval('Unused'), stream[len_cnt:]))
            return False

    def dump(self, res=None, level=0):
        if res is None:
            res = self.result
        for i in res:
            if i.p_sub is not None:
                if i.success:
                    self.dump(i.p_sub, level+1)
                else:
                    print(self.param2str(i))
            else:
                print(self.param2str(i))


if __name__ == '__main__':
    UnpackStream(b'\x04\x3e\x13\x01\x00\x40\x00\x00\x01\x01\x02\x03\x04\x05\xff\x27\x00\x00\x00\xd0\x07\x05').dump()
