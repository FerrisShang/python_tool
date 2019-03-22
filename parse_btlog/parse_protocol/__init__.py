import xlrd
from re import fullmatch
from collections import OrderedDict
from struct import pack, unpack
from enum import Enum


__all__ = [
    'UnpackStream',
    'PackStream'
]


class BasicType(Enum):
    enum = 'enum'
    unsigned = 'unsigned'
    signed = 'signed'
    stream = 'stream'
    hex = 'hex'
    address = 'address'
    T0_625ms = 'T0_625ms'
    T1_25ms = 'T1_25ms'
    T10ms = 'T10ms'
    bitmap = 'bitmap'


class RegExp:
    SHEET_FORMAT_NAME = 'Format(_[A-Za-z][A-Za-z0-9]+)?'
    SHEET_PARAM_NAME = 'Param(_[A-Za-z][A-Za-z0-9]+)?'
    PARAM_NAME = '[A-Za-z][A-Za-z0-9_]*'
    PARAM_WIDTH = '(([A-Za-z][A-Za-z0-9_]+)|([-]?[0-9]+)|([0-9]+/((8)|(16)|(32))))?'
    PARAM_TYPE = PARAM_NAME
    PARAM_KEY = '[A-Za-z][A-Za-z0-9_]+'
    PARAM_SUB_KEY = '(([A-Za-z][A-Za-z0-9_]+)|0)?'
    PARAM_VALUE = '(0x[A-Fa-f0-9]+)|[0-9]+'
    PARAM_RANGE = '(((0x[A-Fa-f0-9]+)|[0-9]+)-((0x[A-Fa-f0-9]+)|[0-9]+)(\|((0x[A-Fa-f0-9]+)|[0-9]+)-((0x[A-Fa-f0-9]+)|[0-9]+))*)?'
    PARAM_DEFAULT = '((0x[A-Fa-f0-9]+)|[-]?[0-9]+)?'
    PARAM_CFG = '(0x[A-Fa-f0-9]+)?'
    FORMAT_PARAM = '[A-Za-z][A-Za-z0-9_]+([ ]+[A-Za-z][A-Za-z0-9_]+)?([ ]*\|[ ]*[A-Za-z][A-Za-z0-9_]+([ ]+[A-Za-z][A-Za-z0-9_]+)?)*'
    PARAM_WIDTH_NUM = '[-]?[0-9]+'
    PARAM_WIDTH_BIT = '[0-9]+/[0-9]+'


class Info:
    def __init__(self, sheet_suffix, sheet_name, line):
        self.sheet_suffix = sheet_suffix
        self.sheet_name = sheet_name
        self.line = line


class ParameterRec:
    class KeyValue:
        def __init__(self, value, description):
            self.value = value
            self.description = description

    def __init__(self, name, width, d_type, sub_key, d_range, default, cfg_flag, description, sheet_suffix, sheet_name, line):
        self.name = name
        self.width = width
        self.type = d_type
        self.sub_key = sub_key
        self.range = d_range
        self.default = default
        self.cfg_flag = cfg_flag
        self.description = description
        self.info = Info(sheet_suffix, sheet_name, line)
        if self.type == BasicType.enum.name or self.type == BasicType.bitmap.name:
            self.key_value = OrderedDict()

    def enum_add(self, key, value, description):
        if not hasattr(self, 'key_value'):
            return False
        if key in self.key_value:
            print('Warning: Parameter {} type enum already has the key {}'.format(self.name, key))
        else:
            self.key_value[key] = self.KeyValue(value, description)
        return True

    def __str__(self):
        string = '{:32s}  {:16s}  {:16s}  {}'.format(self.name, self.width, self.type, self.sub_key)
        if self.type == BasicType.enum.name or self.type == BasicType.bitmap.name:
            for k, v in self.key_value.items():
                string += '\n\t\t{:50s}{:10s}{}'.format(k, v.value, v.description)
        return string


class FormatRec:
    class KeyValue:
        def __init__(self, parameters, remark):
            self.parameters = parameters
            self.remark = remark

    def __init__(self, command, remark, key_code, parameters, sheet_suffix, sheet_name, line):
        self.command = command
        self.key_value = OrderedDict()
        self.info = Info(sheet_suffix, sheet_name, line)
        self.add(remark, key_code, parameters)

    def add(self, remark, key_code, parameters):
        if key_code in self.key_value:
            print('Warning: Format {} already had key {}'.format(self.command, key_code))
        else:
            self.key_value[key_code] = self.KeyValue(parameters, remark)

    def __str__(self):
        string = '{:16s}'.format(self.command)
        for k, v in self.key_value.items():
            string += '{:50}{:16s}{}\n'.format(v.remark, k, v.parameters) + 16*' '
        return string


class ParamData:
    DEFAULT_NAME_FMT = 'Format'
    DEFAULT_NAME_PARAM = 'Param'
    RESERVED_LINE = 1
    (idx_name, idx_width, idx_type, idx_key, idx_sub_key, idx_value, idx_range, idx_default, idx_cfg, idx_desc) = \
        (0, 1, 2, 3, 3, 4, 4, 5, 6, 7)
    (idx_command, idx_remark, idx_key_code, idx_parameters) = (0, 1, 2, 3)

    @staticmethod
    def __regular_check_param__(check_list, params, sheet_name, parsing_line):
        for c in check_list:
            reg, data = c[0], params[eval('ParamData.idx_' + c[1])]
            if fullmatch(reg, data) is None:
                print("Error: Parameter '{}' invalid in Sheet '{}', line {}. Value = {}".
                      format(c[1], sheet_name, parsing_line, repr(data)))
                return False
        return True

    @staticmethod
    def __regular_check_format__(check_list, params, sheet_name, parsing_line):
        for c in check_list:
            reg, data = c[0], params[eval('ParamData.idx_'+c[1])]
            if fullmatch(reg, data) is None:
                print("Error: Column '{}' invalid in Sheet '{}', line {}. Value = {}".
                      format(c[1], sheet_name, parsing_line, repr(data)))
                return False
        return True

    def param_data_to_class(self, param_data, sheet_name):
        last_param = None
        symbol = (sheet_name.split('_')[1]+'_') if '_' in sheet_name else ''
        for i in range(len(param_data)):
            pl = param_data[i]
            if len(pl[self.idx_name]) > 0 and pl[self.idx_name][0] == '#':
                continue
            if pl[self.idx_name] != '':  # parameter definition
                #  parameter define validation
                chk = [(RegExp.PARAM_NAME, 'name'), (RegExp.PARAM_WIDTH, 'width'), (RegExp.PARAM_TYPE, 'type'),
                       (RegExp.PARAM_DEFAULT, 'default'), (RegExp.PARAM_CFG, 'cfg'), ]
                if pl[self.idx_type] != BasicType.enum.name and pl[self.idx_type] != BasicType.bitmap.name:
                    chk += [(RegExp.PARAM_SUB_KEY, 'sub_key'), (RegExp.PARAM_RANGE, 'range')]
                if not self.__regular_check_param__(chk, pl, sheet_name, i+1+self.RESERVED_LINE):
                    return False
                if symbol + pl[self.idx_name] in self.param_dict:
                    print("Error: Parameter {} redefined in Sheet '{}', line {}".format(pl[self.idx_name], sheet_name, i+1+self.RESERVED_LINE))
                    return False
                width_trans = pl[self.idx_width]
                if fullmatch(RegExp.PARAM_WIDTH_NUM, width_trans) is None and fullmatch(RegExp.PARAM_WIDTH_BIT, width_trans) is None:
                    if symbol + width_trans in self.param_dict:
                        width_trans = symbol + width_trans
                type_trans = pl[self.idx_type] if symbol + pl[self.idx_type] not in self.param_dict else symbol + pl[self.idx_type]
                sub_key_trans = pl[self.idx_sub_key] if symbol + pl[self.idx_sub_key] not in self.param_dict else symbol + pl[self.idx_sub_key]
                last_param = self.param_dict[symbol+pl[self.idx_name]] = \
                    ParameterRec(pl[self.idx_name], width_trans, type_trans, sub_key_trans,
                                 pl[self.idx_range], pl[self.idx_default], pl[self.idx_cfg], pl[self.idx_desc], symbol, sheet_name, i+1+self.RESERVED_LINE)
            if (pl[self.idx_name] != '' and (pl[self.idx_type] == BasicType.enum.name or pl[self.idx_type] == BasicType.bitmap.name)) or \
                    (pl[self.idx_name], pl[self.idx_width], pl[self.idx_type]) == ('', '', ''):  # enum value, key
                #  enum value, key validation
                chk = [(RegExp.PARAM_KEY, 'key'), (RegExp.PARAM_VALUE, 'value')]
                if not self.__regular_check_param__(chk, pl, sheet_name, i+1+self.RESERVED_LINE):
                    return False
                if last_param is None:
                    print("Error: Invalid definition in Sheet '{}', line {}".format(sheet_name, i+1+self.RESERVED_LINE))
                    return False
                if int(pl[self.idx_value], 0) in [int(v.value, 0) for k, v in last_param.key_value.items()] or \
                        pl[self.idx_key] in last_param.key_value:
                    print("Error: Key value redefinition in Sheet '{}', line {}".format(sheet_name, i+1+self.RESERVED_LINE))
                    return False
                last_param.enum_add(pl[self.idx_key], pl[self.idx_value], pl[self.idx_desc])
            if not (pl[self.idx_name] != '' or (pl[self.idx_name], pl[self.idx_width], pl[self.idx_type], pl[self.idx_type]) == ('', '', '', '')):
                print("Warning: Parse failed in Sheet '{}', line {}".format(sheet_name, i+1+self.RESERVED_LINE))
        return True

    def format_data_to_class(self, format_data, sheet_name):
        last_format = None
        symbol = (sheet_name.split('_')[1]+'_') if '_' in sheet_name else ''
        for i in range(len(format_data)):
            fl = format_data[i]
            if len(fl[self.idx_command]) > 0 and fl[self.idx_command][0] == '#':
                continue
            if fl[self.idx_command] != '' and fl[self.idx_key_code] != '' and fl[self.idx_parameters] != '':  # First line definition
                #  validation
                chk = [(RegExp.PARAM_NAME, 'command'), (RegExp.PARAM_VALUE, 'key_code'), (RegExp.FORMAT_PARAM, 'parameters')]
                if not self.__regular_check_format__(chk, fl, sheet_name, i+1+self.RESERVED_LINE):
                    return False
                # save format
                command_tran = symbol + fl[self.idx_command]
                if command_tran in self.format_dict:
                    print('Warning: Format {} redefined'.format(fl[self.idx_command]))
                else:
                    last_format = self.format_dict[command_tran] = FormatRec(fl[self.idx_command], fl[self.idx_remark], fl[self.idx_key_code],
                                                                             fl[self.idx_parameters], symbol, sheet_name, i+1+self.RESERVED_LINE)
            elif fl[self.idx_command] == '' and fl[self.idx_key_code] != '' and fl[self.idx_parameters] != '' and last_format is not None:
                #  validation
                chk = [(RegExp.PARAM_VALUE, 'key_code'), (RegExp.FORMAT_PARAM, 'parameters')]
                if not self.__regular_check_format__(chk, fl, sheet_name, i+1+self.RESERVED_LINE):
                    return False
                # save
                last_format.add(fl[self.idx_remark], fl[self.idx_key_code], fl[self.idx_parameters])
            else:
                print("Warning: Parse failed in Sheet '{}', line {}".format(sheet_name, i+1+self.RESERVED_LINE))
        return True

    def format_to_param(self):
        # """Auto generate"""
        fmt_name = [k for k, v in self.format_dict.items()]
        param_name = [name for name, fmt in self.param_dict.items()]
        for name in set(fmt_name) - set(param_name):
            # print(self.format_dict[name].key_value)
            if name not in self.param_dict and '0' in self.format_dict[name].key_value and len(self.format_dict[name].key_value) == 1:
                self.param_dict[name] = ParameterRec('auto_gen_'+name, '0', 'stream', '0', '', '', '', '', '', '', 0)

    def read(self, filename):
        book = xlrd.open_workbook(filename)
        proto_names = list('')
        for sheet_name in book.sheet_names():
            if fullmatch(RegExp.SHEET_FORMAT_NAME, sheet_name) or fullmatch(RegExp.SHEET_PARAM_NAME, sheet_name):
                symbol = sheet_name.split('_')[1] if '_' in sheet_name else ''
                if symbol not in proto_names:
                    proto_names.append(symbol)
        for name in proto_names:
            # sheet name validation
            if name == '':
                fmt_name, param_name = self.DEFAULT_NAME_FMT, self.DEFAULT_NAME_PARAM
            else:
                fmt_name, param_name = self.DEFAULT_NAME_FMT+'_'+name, self.DEFAULT_NAME_PARAM+'_'+name
            if fmt_name not in book.sheet_names() or param_name not in book.sheet_names():
                print('Error: Sheet "{}" or "{}" not found in file'.format(fmt_name, param_name))
                return False
            sheet_format = book.sheet_by_name(fmt_name)
            sheet_param = book.sheet_by_name(param_name)
            format_data = [sheet_format.row_values(i) for i in range(self.RESERVED_LINE, sheet_format.nrows)]
            format_data = [[str(int(a)) if type(a) == float else str(a).strip() for a in j] for j in format_data]
            param_data = [sheet_param.row_values(i) for i in range(self.RESERVED_LINE, sheet_param.nrows)]
            param_data = [[str(int(a)) if type(a) == float else str(a).strip() for a in j] for j in param_data]
            if not self.param_data_to_class(param_data, param_name) or not self.format_data_to_class(format_data, fmt_name):
                return False
        self.format_to_param()
        return True

    def validation(self):
        for name, param in self.param_dict.items():  # parameters
            assert(isinstance(param, ParameterRec))
            # validate bit width
            if fullmatch(RegExp.PARAM_WIDTH_BIT, param.width) is not None:  # bit width
                n1, n2 = [int(x) for x in param.width.split('/')]
                if not (n2 > n1 > 0 and n2 % 8 == 0):
                    print("Error: Param '{}' bit_width invalid. Sheet '{}', line {}".format(param.name, param.info.sheet_name, param.info.line))
                    return False
            elif param.width != '' and fullmatch(RegExp.PARAM_WIDTH_NUM, param.width) is None:  # parameter name
                if param.width not in self.param_dict:
                    print("Error: Param '{}' bit_width invalid, param '{}' not defined. Sheet '{}', line {}".
                          format(param.name, param.width, param.info.sheet_name, param.info.line))
                    return False
                if self.param_dict[param.width].type != BasicType.unsigned.name:
                    print("Error: Param '{}' bit_width invalid, bit_width param must be the unsigned type. Sheet '{}', line {}".
                          format(param.name, param.info.sheet_name, param.info.line))
                    return False
                if param.width == param.name:
                    print("Error: Param '{}' bit_width invalid, width can NOT reference itself. Sheet '{}', line {}".
                          format(param.name, param.width, param.info.sheet_name, param.info.line))
                    return False
            elif param.width == '' and param.type in [t.name for t in BasicType]:
                print("Error: Param '{}' bit_width can NOT be empty. Sheet '{}', line {}".
                      format(param.name, param.width, param.info.sheet_name, param.info.line))
                return False
            # validate type
            if param.type not in [p.name for p in BasicType]:
                if param.type not in self.param_dict:
                    print("Error: Param '{}' type invalid, param '{}' is not a valid BasicType or not defined. Sheet '{}', line {}".
                          format(param.name, param.type, param.info.sheet_name, param.info.line))
                    return False
                else:
                    check_list = [param.width, param.sub_key, param.range, param.default, param.cfg_flag, param.description]
                    if sum([0 if check == '' else 1 for check in check_list]) > 0:
                        print("Warning: Param '{}' is reference to '{}' which is not a BasicType, All column should be empty except name & type. Sheet '{}', line {}".
                              format(param.name, param.type, param.info.sheet_name, param.info.line))
            if param.type == param.name:
                print("Error: Param '{}' type invalid, type can NOT reference itself. Sheet '{}', line {}".
                      format(param.name, param.width, param.info.sheet_name, param.info.line))
                return False
            # sub_key
            if param.type != BasicType.enum.name and param.type != BasicType.bitmap.name and param.sub_key != '' and param.sub_key != '0':
                if param.sub_key not in self.param_dict:
                    print("Error: Param '{}' sub_key invalid, '{}' is not defined. Sheet '{}', line {}".
                          format(param.name, param.sub_key, param.info.sheet_name, param.info.line))
                    return False
                elif self.param_dict[param.sub_key].type != BasicType.enum.name and self.param_dict[param.sub_key].type != BasicType.enum.name:
                    print("Error: Param '{}' sub_key invalid, sub_key param must be the enum type. Sheet '{}', line {}".
                          format(param.name, param.info.sheet_name, param.info.line))
                    return False
        for name, fmt in self.format_dict.items():  # formats
            assert(isinstance(fmt, FormatRec))
            if name not in self.param_dict:
                print("Warning: Format '{}' not defined as parameter. Sheet '{}', line {}".
                      format(fmt.command, fmt.info.sheet_name, fmt.info.line))
            elif self.param_dict[name].sub_key == '':
                print("Warning: Format '{}' defined but parameter {} maybe missing the sub_key. Sheet '{}', line {}".
                      format(fmt.command, fmt.command, fmt.info.sheet_name, fmt.info.line))
            for k, item in fmt.key_value.items():
                assert(isinstance(item, FormatRec.KeyValue))
                param_list = [p.split()[0] for p in item.parameters.split('|')]
                for param in param_list:
                    if param not in self.param_dict and fmt.info.sheet_suffix + param not in self.param_dict:
                        print("Error: Format {} invalid, Param '{}' not defined. Sheet '{}', line {}".
                              format(fmt.command, param, fmt.info.sheet_name, fmt.info.line))
                        return False
            fmt_keys = [k for k, v in fmt.key_value.items()]
            sub_key = self.param_dict[name].sub_key
            if sub_key == '0':
                param_values = ['0']
            else:
                param_values = [v.value for k, v in self.param_dict[sub_key].key_value.items()]
            if len(fmt_keys) != len(param_values):
                print("Error: Format {} invalid, the number of items in Param {}'s sub_key {} is different. Sheet '{}', line {}".
                      format(fmt.command, self.param_dict[name].name, self.param_dict[sub_key].name, fmt.info.sheet_name, fmt.info.line))
                return False
            for a, b in zip(fmt_keys, param_values):
                if int(a, 0) != int(b, 0):
                    print("Error: Format {} invalid, enum value and sub_key {}'s value is different. Sheet '{}', line {}".
                          format(fmt.command, self.param_dict[name].name, fmt.info.sheet_name, fmt.info.line))
                    return False

        #  Unused check
        params_in_format = {'PROTO_ALL'}
        formats = set()
        for name, fmt in self.format_dict.items():
            symbol = fmt.info.sheet_suffix
            for k, item in fmt.key_value.items():
                params_list = [type_desc.split()[0] for type_desc in item.parameters.split('|')]
                params_list = [p if symbol + p not in self.param_dict else symbol + p for p in params_list]
                params_in_format |= set(params_list)
                formats.add(name)
        params_in_type = set([p.type for k, p in self.param_dict.items()])
        params_in_sub_key = set([p.sub_key for k, p in self.param_dict.items()])
        params_in_param_name = set([k for k, p in self.param_dict.items()])
        params_have_sub_key = set()
        for name, fmt in self.param_dict.items():
            assert(isinstance(fmt, ParameterRec))
            if fmt.sub_key != '' and fmt.type != BasicType.enum.name and fmt.type != BasicType.bitmap.name:
                params_have_sub_key.add(name)
        for undefined in params_have_sub_key - formats:
            param = self.param_dict[undefined]
            print("Error: Format {} undefined. Sheet '{}', line {}".format(param.name, param.info.sheet_name, param.info.line))
            return False
        for unused in (params_in_param_name - (params_in_format | params_in_type | params_in_sub_key)):
            param = self.param_dict[unused]
            print("Warning: Unused parameter '{}'. Sheet '{}', line {}".format(param.name, param.info.sheet_name, param.info.line))
        return True

    def __get_param_desc_from_string(self, string, sheet_suffix):
        items = [x for x in string.split('|')]
        param_names = [x.split()[0] for x in items]
        params_list_str = [p if sheet_suffix + p not in self.param_dict else sheet_suffix + p for p in param_names]
        desc_list_str = [repr(x.split()[1]) if len(x.split()) == 2 else repr('') for x in items]
        return ', '.join(["({}, {})".format(p, d) for p, d in zip(params_list_str, desc_list_str)])

    def to_code(self):
        if not self.parse_suc:
            return ''
        if not self.validation():
            return ''
        code_lines = 'from enum import Enum\n\n\n'
        param_str_dict = OrderedDict()
        for name, param in self.param_dict.items():  # parameters
            assert(isinstance(param, ParameterRec))
            if param.type not in [t.name for t in BasicType]:  # Define parameter by other one
                param_str_dict[name] = param_str_dict[param.type].replace('class {}'.format(param.type), 'class {}'.format(name))
                continue
            param_str = ''
            param_str += 'class {}{}:\n'.format(name, '' if (param.type != BasicType.enum.name and param.type != BasicType.bitmap.name) else '(Enum)')
            if fullmatch(RegExp.PARAM_WIDTH_NUM, param.width):
                param_str += '    __bit_width__ = {}\n'.format(int(param.width))
            elif param.width != '':
                param_str += '    __bit_width__ = {}\n'.format(repr(param.width))
            param_str += '    __data_type__ = {}\n'.format(repr(param.type))
            if len(param.default) > 0:
                param_str += '    __default__ = {}\n'.format(param.default)
            if len(param.cfg_flag) > 0:
                param_str += '    __cfg_flag__ = {}\n'.format(param.cfg_flag)
            if param.type != BasicType.enum.name and param.type != BasicType.bitmap.name:
                if len(param.range) > 0:
                    param_str += '    __range__ = {}\n'.format(repr(param.range))
                if len(param.sub_key) > 0:
                    param_str += '    __sub_key__ = {}\n'.format(repr(param.sub_key))
                if len(param.description) != 0:
                    param_str += '    __description__ = {}\n'.format(repr(param.description))
            else:
                for k, v in param.key_value.items():
                    assert(isinstance(v, ParameterRec.KeyValue))
                    param_str += '    {} = {}\n'.format(k, v.value)
                    if len(v.description) != 0:
                        param_str += '    __Des_{}__ = {}\n'.format(k, repr(v.description))
            param_str += '\n\n'
            param_str_dict[name] = param_str
        for k, v in param_str_dict.items():
            code_lines += v
        for name, fmt in self.format_dict.items():  # formats
            assert(isinstance(fmt, FormatRec))
            code_lines += 'fmt_{}'.format(name) + ' = {\n'
            sub_key_type = self.param_dict[name].sub_key
            if sub_key_type == '0':
                string = [v.parameters for k, v in fmt.key_value.items()][0]
                pair_list_str = self.__get_param_desc_from_string(string, fmt.info.sheet_suffix)
                code_lines += '    {}: ({}),\n'.format(sub_key_type, pair_list_str)
            else:
                fmt_item_list = [v for k, v in fmt.key_value.items()]
                enum_item_list = [k for k, v in self.param_dict[sub_key_type].key_value.items()]
                assert(len(fmt_item_list) == len(enum_item_list))
                for fmt_item, enum_item in zip(fmt_item_list, enum_item_list):
                    assert(isinstance(fmt_item, FormatRec.KeyValue))
                    assert(isinstance(enum_item, str))
                    key_str = '{}.{}'.format(sub_key_type, enum_item)
                    pair_list_str = self.__get_param_desc_from_string(fmt_item.parameters, fmt.info.sheet_suffix)
                    code_lines += '    {}: ({},),\n'.format(key_str, pair_list_str)
            code_lines += '}\n'
        return code_lines

    def to_file(self, filename='param.py'):
        code_lines = self.to_code()
        with open(filename, 'w') as f:
            f.write(code_lines)
            f.close()
        return code_lines

    def __init__(self, filename='parse_protocol/parse.xlsx'):
        self.proto_sheet_names = []
        self.format_dict = OrderedDict()
        self.param_dict = OrderedDict()
        self.parse_suc = self.read(filename)

    def dump(self):
        for n, p in self.param_dict.items():
            print(p)
        for n, p in self.format_dict.items():
            print(p)


try:
    __code_lines__ = ParamData().to_file()
    if __code_lines__ != '':
        exec(__code_lines__)
    else:
        from param import *
except FileNotFoundError:
    from param import *


class UnpackStream:
    bit_output_sub_key = 0x01
    bit_inc_indent = 0x02
    bit_bitmap_output_0 = 0x04
    bit_ignore_extra_param = 0x08

    class Item:
        def __init__(self, p_class, value, length, alias='', sub_item=None, bit_pos=0):
            self.type = p_class
            self.value = value
            self.length = length  # value length
            self.sub_item = sub_item
            self.alias = alias
            self.bit_pos = bit_pos

    class ParseError(Exception):
        pass

    @staticmethod
    def time_trans(value_bytes, time_base):
        return (str(int.from_bytes(value_bytes, 'little') * time_base) + ' ms').replace('.0 ms', ' ms').replace('000 ms', ' s')

    @staticmethod
    def param_to_str(item, indent):
        title_length = 40
        assert(isinstance(item, UnpackStream.Item))
        if item.alias != '':
            title_str = item.alias
        else:
            if hasattr(item.type, '__description__'):
                title_str = eval(item.type.__name__+'.__description__')
            else:
                title_str = item.type.__name__.replace('_', ' ')
        if item.value is None:
            if hasattr(item.type, '__cfg_flag__') and item.type.__cfg_flag__ & UnpackStream.bit_ignore_extra_param > 0:
                return ''
            else:
                return ' ' * 4 * (1 + indent) + ('{:%ds}: {}' % (title_length - 4 * indent)).format(title_str, 'Warning(No More Data !)')
        data_str = []
        try:
            p_type = item.type.__data_type__
            p_length = item.length if not (isinstance(item.type.__bit_width__, str) and '/' in item.type.__bit_width__)\
                else (int(item.type.__bit_width__.split('/')[0]) + 7) // 8
            unpack_len = item.length
            if p_type == 'unsigned':
                unsigned_unpack = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}
                data_str.append(str(unpack(unsigned_unpack[unpack_len], item.value)[0]))
            elif p_type == 'signed':
                signed_unpack = {1: 'b', 2: 'h', 4: 'i', 8: 'q'}
                data_str.append(str(unpack(signed_unpack[unpack_len], item.value)[0]))
            elif p_type == 'stream':
                data_str.append(''.join('{:02X} '.format(x) for x in item.value))
            elif p_type == 'hex':
                data_str.append(''.join(('0x{:0%dX}' % (p_length * 2)).format(int.from_bytes(item.value, 'little'))))
            elif p_type == 'address':
                data_str.append(':'.join('{:02X}'.format(x) for x in item.value[::-1]))
            elif p_type == 'T0_625ms':
                data_str.append(''.join(('0x{:0%dX}' % (p_length * 2)).format(int.from_bytes(item.value, 'little'))) +
                                ' ({})'.format(UnpackStream.time_trans(item.value, 0.625)))
            elif p_type == 'T1_25ms':
                data_str.append(''.join(('0x{:0%dX}' % (p_length * 2)).format(int.from_bytes(item.value, 'little'))) +
                                ' ({})'.format(UnpackStream.time_trans(item.value, 1.25)))
            elif p_type == 'T10ms':
                data_str.append(''.join(('0x{:0%dX}' % (p_length * 2)).format(int.from_bytes(item.value, 'little'))) +
                                ' ({})'.format(UnpackStream.time_trans(item.value, 10)))
            elif p_type == 'enum':
                value, enum_value = int.from_bytes(item.value, 'little'), [c.value for c in item.type]
                if value in enum_value and hasattr(item.type, '__Des_{}__'.format(item.type(value).name)):
                    tmp_str = eval(item.type.__name__+'.__Des_{}__'.format(item.type(value).name))
                else:
                    tmp_str = str(item.type(int.from_bytes(item.value, 'little')).name)
                tmp_str += ' (' + ''.join('0x{:02X}'.format(int.from_bytes(item.value, 'little'))) + ')'
                data_str.append(tmp_str)
            elif p_type == 'bitmap':
                value, enum_value = int.from_bytes(item.value, 'little'), [c.value for c in item.type]
                data_str.append(("{:0%db}  " % (p_length * 8)).format(int.from_bytes(item.value, 'little')) +
                                ''.join(('0x{:0%dX}' % (p_length * 2)).format(int.from_bytes(item.value, 'little'))))
                for i in range(max(enum_value)+1):
                    try:
                        if value & (1 << i) != 0 or (hasattr(item.type, '__cfg_flag__') and item.type.__cfg_flag__ & UnpackStream.bit_bitmap_output_0 > 0):
                            dots = ['.' for _ in range(p_length * 8)]
                            dots[-1 - i] = '1' if (value & (1 << i)) > 0 else '0'
                            if i in enum_value and hasattr(item.type, '__Des_{}__'.format(item.type(i).name)):
                                tmp_str = ''.join(dots) + '  ' + eval(item.type.__name__+'.__Des_{}__'.format(item.type(i).name))
                            else:
                                tmp_str = ''.join(dots) + '  ' + str(item.type(i).name)
                            data_str.append(tmp_str)
                    except ValueError:
                        pass
            else:
                raise ValueError
        except ValueError:
            data_str.append(''.join('{:02X} '.format(x) for x in item.value) + ' (Unknown)')

        bit_cnt = bit_width = 0  # use for bit map parameters
        if isinstance(item.type.__bit_width__, str):
            assert('/' in item.type.__bit_width__)
            bit_cnt, bit_width = [int(x) for x in item.type.__bit_width__.split('/')]
        if bit_cnt > 0 and bit_width > 0:
            title_str += ' (bit[' + str(bit_width - item.bit_pos - 1) + \
                         ('])' if bit_cnt == 1 else ':{}])'.format(bit_width - item.bit_pos - bit_cnt))
        ret_str = ' ' * 4 * (1+indent) + ('{:%ds}: {}' % (title_length-4*indent)).format(title_str, data_str[0])
        for i in range(1, len(data_str)):
            ret_str += '\n' + ' ' * (4 * (1+indent) + title_length + 2) + data_str[i]
        return ret_str

    def __init__(self, stream):
        self.stream = stream
        self.result = self.unpack(stream)

    def unpack(self, stream):
        parse_result = self.__unpack__(stream)
        # Adjust recursive parameters
        self.__adjust_recursive_param__(parse_result)
        return parse_result

    def __adjust_recursive_param__(self, parse_result):
        list_len = len(parse_result)
        idx = 0
        while idx < list_len:
            param = parse_result[idx]
            assert(isinstance(param, self.Item))
            if param.sub_item is not None:
                for sub_idx in range(len(param.sub_item)):
                    if param.type == param.sub_item[sub_idx].type:
                        sub_item_value_len = 0 if param.sub_item[sub_idx].value is None else len(param.sub_item[sub_idx].value)
                        param.value = param.value[:-sub_item_value_len]
                        parse_result.insert(idx+1, param.sub_item[sub_idx])
                        param.sub_item.remove(param.sub_item[sub_idx])
                        list_len += 1
                        break
                self.__adjust_recursive_param__(param.sub_item)
            idx += 1

    def __unpack__(self, stream, unpack_fmt=None, key=None, parse_rec=None):
        if unpack_fmt is None:
            (unpack_fmt, key, parse_rec) = (eval('fmt_PROTO_ALL'), 0, [])
        assert(isinstance(parse_rec, list))
        parse_result = []
        pc = 0  # parsing current pos by byte
        bit_pos = bit_all = 0  # only use for param with bit_width is 'a/b'
        try:
            for p_class, alias in unpack_fmt[key]:
                if pc == len(stream):
                    item = self.Item(p_class, None, 0, alias)
                    parse_result.append(item)
                    parse_rec.append(item)
                    continue
                if isinstance(p_class.__bit_width__, str) and fullmatch(RegExp.PARAM_WIDTH_BIT, p_class.__bit_width__) is None or\
                        isinstance(p_class.__bit_width__, int):  # param for length or number for length
                    bit_pos = 0  # reset bit_pos
                    if isinstance(p_class.__bit_width__, int):
                        p_len = (p_class.__bit_width__ // 8) if p_class.__bit_width__ != 0 else len(stream[pc:])
                    else:
                        assert(isinstance(p_class.__bit_width__, str))
                        class_type = globals()[p_class.__bit_width__]
                        p_len = -1
                        for rec in parse_rec[::-1]:
                            assert(isinstance(rec, UnpackStream.Item))
                            if rec.type == class_type:
                                p_len = int.from_bytes(rec.value, 'little')
                                break
                        if p_len < 0:
                            raise UnpackStream.ParseError
                    if pc + p_len > len(stream):
                        item = self.Item(p_class, None, 0, alias)
                    elif hasattr(p_class, '__sub_key__'):
                        item = self.Item(p_class, stream[pc:pc+p_len], p_len, alias, [])
                    else:
                        item = self.Item(p_class, stream[pc:pc+p_len], p_len, alias)
                    pc += p_len
                    parse_result.append(item)
                    parse_rec.append(item)
                else:  # param's length counts by bits
                    assert('/' in p_class.__bit_width__)
                    cnt, bit_all = [int(num, 0) for num in p_class.__bit_width__.split('/')]
                    p_len = bit_all // 8
                    if pc + p_len > len(stream):
                        item = self.Item(p_class, stream[pc:], len(stream[pc:]), alias)
                        parse_result.append(item)
                        parse_rec.append(item)
                        pc += len(stream[pc:])
                        break
                    else:
                        unsigned_pack = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}
                        value_bytes = stream[pc:pc+p_len]
                        value = int.from_bytes(value_bytes, 'little')
                        value = (value >> (bit_all - cnt - bit_pos)) & ~((-1) << cnt)
                        value_bytes = pack('<' + unsigned_pack[p_len], value)
                        item = self.Item(p_class, value_bytes, p_len, alias)
                        item.bit_pos = bit_pos
                        parse_result.append(item)
                        parse_rec.append(item)
                        bit_pos += cnt
                        if bit_pos >= bit_all:
                            bit_pos = 0
                            pc += p_len
            if 0 < bit_pos < bit_all:  # bit_width not full used, Adjust pc to skip bytes
                pc += bit_all // 8
            if pc < len(stream):
                item = self.Item(eval('Unused'), stream[pc:], len(stream[pc:]))
                parse_result.append(item)
                parse_rec.append(item)
            for item in parse_result:
                assert(isinstance(item, UnpackStream.Item))
                if item.sub_item is not None:
                    try:
                        if item.type.__sub_key__ == '0':
                            sub_key = 0
                        else:
                            sub_key = None
                            for find_k in parse_result:
                                if find_k.type.__name__ == item.type.__sub_key__:
                                    sub_key = int.from_bytes(find_k.value, 'little')
                                    sub_key = find_k.type(sub_key)
                                    break
                        item.sub_item = self.__unpack__(item.value, eval('fmt_' + item.type.__name__), sub_key, parse_rec)
                    except ValueError:
                        item.sub_item = None
        except ValueError:
            if pc < len(stream):
                parse_result.append(self.Item(eval('Unused'), stream[pc:], len(stream[pc:])))
        return parse_result

    def to_string(self, res=None, level=0, indent=0):
        string_ret = ''
        if res is None:
            string_ret += ''.join('{:02X} '.format(x) for x in self.stream) + '\n'
            res = self.result
        for i in res:
            if i.sub_item is not None:
                if hasattr(i.type, '__cfg_flag__') and i.type.__cfg_flag__ & self.bit_output_sub_key > 0:
                    string_ret += self.param_to_str(i, indent) + '\n'
                ind = 1 if hasattr(i.type, '__cfg_flag__') and i.type.__cfg_flag__ & self.bit_inc_indent > 0 else 0
                string_ret += self.to_string(i.sub_item, level + 1, indent + ind)
            else:
                string_ret += self.param_to_str(i, indent) + '\n'
        return string_ret

    def dump(self, res=None, level=0, indent=0):
        if res is None:
            res = self.result
        for i in res:
            assert(isinstance(i, self.Item))
            print(' ' * 4 * indent, end='')
            print(i.type.__name__, i.value)
            if i.sub_item is not None:
                self.dump(i.sub_item, level+1, indent+1)


class PackStream:
    bit_output_sub_key = 0x01
    bit_inc_indent = 0x02
    bit_bitmap_output_0 = 0x04
    bit_ignore_extra_param = 0x08
    bit_param_for_length = 0x10
    def __init__(self, *args):
        self.init_args = list(args)
        self.parse_rec = None
        self.init_pack = self.pack(self.init_args)
        self.__cal_length__()

    def __pack__(self, args, pack_fmt=None, parse_rec=None):
        if pack_fmt is None:
            pack_fmt = eval('fmt_PROTO_ALL[0]')
            self.parse_rec = [None for _ in range(len(pack_fmt))]
            parse_rec = self.parse_rec
        if not isinstance(args, list):
            print('Error: Args must be list but {} found -> {}'.format(type(args), args))
            args = []
        args = args[:len(pack_fmt)] + [None for _ in range(len(pack_fmt)-len(args))]
        for i in range(len(parse_rec)):
            if args[i] is None:
                args[i] = self.Undefined()
            parse_rec[i] = self.Rec(FormatRec.KeyValue(*pack_fmt[i]), args[i])
        self.__check_data__(parse_rec)
        for i in range(len(parse_rec)):
            # Check sub format if class has sub_key
            if hasattr(parse_rec[i].class_type.parameters, '__sub_key__'):
                if parse_rec[i].class_type.parameters.__sub_key__ == '0':
                    sub_key = 0
                else:
                    sub_key = None
                    tmp_rec = []  # save all level parameters in tmp_rec
                    rec_list = [self.parse_rec]
                    while len(rec_list) > 0:
                        cur_rec = rec_list.pop()
                        tmp_rec += cur_rec[:]
                        if parse_rec[i].class_type.parameters.__sub_key__ in [c.class_type.parameters.__name__ for c in cur_rec]:
                            break
                        for r in cur_rec:
                            if r.sub_rec is not None:
                                rec_list.insert(0, r.sub_rec)

                    for find_k in tmp_rec[::-1]:
                        assert(isinstance(find_k, self.Rec))
                        if find_k.class_type.parameters.__name__ == parse_rec[i].class_type.parameters.__sub_key__:
                            if isinstance(find_k.value, bytes):
                                sub_key = int.from_bytes(find_k.value, 'little')
                            else:
                                sub_key = find_k.value
                            try:
                                sub_key = find_k.class_type.parameters(sub_key)
                            except ValueError:
                                sub_key = None
                            break
                if sub_key is not None:
                    sub_format = eval('fmt_' + parse_rec[i].class_type.parameters.__name__ + '[{}]'.format(sub_key))
                    parse_rec[i].sub_format = list(sub_format)
                    parse_rec[i].sub_rec = [None for _ in range(len(parse_rec[i].sub_format))]
                    if type(parse_rec[i].value) == self.Undefined:
                        parse_rec[i].value = []
                else:
                    parse_rec[i].value = self.Undefined()
        for i in range(len(parse_rec)):
            if parse_rec[i].sub_format is not None:
                self.__pack__(parse_rec[i].value, parse_rec[i].sub_format, parse_rec[i].sub_rec)

    def pack(self, args):
        self.__pack__(args)
        return self.parse_rec

    @staticmethod
    def int2bytes(value, bytes_num):  # little-endian
        from binascii import unhexlify
        res = unhexlify(('%%0%dx' % (bytes_num*2)) % max(0, value))[::-1]
        return res

    def __check_data__(self, parse_rec=None):
        if parse_rec is None:
            parse_rec = self.parse_rec
        for i in range(len(parse_rec)):
            assert(isinstance(parse_rec[i].class_type, FormatRec.KeyValue))

            # Integer to bytes
            if isinstance(parse_rec[i].value, int):
                if isinstance(parse_rec[i].class_type.parameters.__bit_width__, int) and \
                        parse_rec[i].class_type.parameters.__bit_width__ > 0:
                    parse_rec[i].value = self.int2bytes(parse_rec[i].value, parse_rec[i].class_type.parameters.__bit_width__ // 8)
                else:
                    parse_rec[i].value = self.int2bytes(parse_rec[i].value, 2)  # tmp
                    pass  # TODO: width is bits or Param or other conditions
            elif isinstance(parse_rec[i].value, list):
                if not hasattr(parse_rec[i].class_type.parameters, '__sub_key__'):
                    parse_rec[i].value = self.Undefined()
            elif not isinstance(parse_rec[i].value, bytes) and not isinstance(parse_rec[i].value, self.Undefined):
                raise self.DataError('Error value type {}:{}'.format(parse_rec[i].value, type(parse_rec[i].value)))

            # Check if enum key value is valid
            if parse_rec[i].class_type.parameters.__data_type__ == 'enum':
                try:
                    if isinstance(parse_rec[i].value, self.Undefined):
                        continue
                    value = int.from_bytes(parse_rec[i].value, 'little')
                    parse_rec[i].class_type.parameters(value)
                except ValueError:
                    print('ValueError: {} is not a valid value of {}'.format(parse_rec[i].value, parse_rec[i].class_type.parameters.__name__))
                    pass
            if isinstance(parse_rec[i].class_type.parameters.__bit_width__, int) and \
                    parse_rec[i].class_type.parameters.__bit_width__ <= 0:
                pass
            else:
                pass  # TODO: check data length

            if parse_rec[i].sub_rec is not None:
                self.__check_data__(parse_rec[i].sub_rec)

    def __cal_length__(self):
        tmp_rec = []  # save all level parameters in tmp_rec
        rec_list = [self.parse_rec]
        while len(rec_list) > 0:
            cur_rec = rec_list.pop()
            tmp_rec += cur_rec[:]
            for r in cur_rec:
                if r.sub_rec is not None:
                    rec_list.insert(0, r.sub_rec)
        sum_length = 0
        for r in tmp_rec[::-1]:
            assert(isinstance(r, self.Rec))
            if hasattr(r.class_type.parameters, '__cfg_flag__') and r.class_type.parameters.__cfg_flag__ & PackStream.bit_param_for_length > 0:
                if not hasattr(r.class_type.parameters, '__default__'):
                    print('Error: Parameter {} miss attribute __default__'.format(r.class_type.parameters.__name__))
                else:
                    r.value = self.int2bytes(r.class_type.parameters.__default__ + sum_length, r.class_type.parameters.__bit_width__//8)
            elif r.sub_format is None and not isinstance(r.value, self.Undefined):
                sum_length += len(r.value)

    def get_rec_list(self, rec=None, dump=None):
        if rec is None:
            rec = self.parse_rec
            dump = []
        for r in rec:
            assert(isinstance(r, self.Rec))
            if r.sub_format is not None:
                self.get_rec_list(r.sub_rec, dump)
            else:
                dump.append(r)
        return dump

    def dump_rec(self, rec=None, dump=None):
        if rec is None:
            rec = self.parse_rec
            dump = []
        for r in rec:
            assert(isinstance(r, self.Rec))
            # value = ''.join('{:02X} '.format(x) for x in r.value)
            if r.sub_format is not None:
                self.dump_rec(r.sub_rec, dump)
            else:
                if isinstance(r.value, self.Undefined):
                    if r.class_type.remark != '':
                        title_str = r.class_type.remark
                    else:
                        if hasattr(r.class_type.parameters, '__description__'):
                            title_str = eval(r.class_type.parameters.__name__+'.__description__')
                        else:
                            title_str = r.class_type.parameters.__name__.replace('_', ' ')
                    output = '    {:40s}: {}'.format(title_str, str(r.value))
                else:
                    output = UnpackStream.param_to_str(UnpackStream.Item(r.class_type.parameters, r.value, len(r.value)), 0)
                print(output)
                dump.append(output)
        return dump

    def to_stream(self, rec=None):
        result = b''
        if rec is None:
            rec = self.parse_rec
        for r in rec:
            if isinstance(r.value, self.Undefined) or r.value is None:
                return None
            elif r.sub_format is not None:
                res = self.to_stream(r.sub_rec)
                if res is None:
                    return None
                result += res
            else:
                result += r.value
        return result

    def to_input_arg(self, rec=None, result=None):
        if rec is None:
            result = []
            rec = self.parse_rec
            self.__check_data__()
            self.__cal_length__()
        for r in rec:
            if isinstance(r.value, self.Undefined):
                result.append(None)
            elif r.sub_format is not None:
                result.append([])
                self.to_input_arg(r.sub_rec, result[-1])
            else:
                result.append(r.value)
        return result

    class Rec:
        enum_get = None
        value_get = None
        bitmap_get = None
        def __init__(self, class_type, value, sub_format=None, sub_rec=None):
            self.class_type = class_type
            self.value = value
            self.sub_format = sub_format
            self.sub_rec = sub_rec

        def input(self):
            assert(isinstance(self.class_type, FormatRec.KeyValue))
            if self.class_type.parameters.__data_type__ == BasicType.enum.name or self.class_type.parameters.__data_type__ == BasicType.bitmap.name:
                param_dict = OrderedDict()
                for e in self.class_type.parameters:
                    if  hasattr(self.class_type.parameters, '__Des_{}__'.format(e.name)):
                        tmp_str = eval(self.class_type.parameters.__name__+'.__Des_{}__'.format(e.name))
                    else:
                        tmp_str = e.name
                    param_dict[e.value] = tmp_str
                if self.class_type.parameters.__data_type__ == BasicType.enum.name:
                    if PackStream.Rec.enum_get is not None:
                        self.value = PackStream.Rec.enum_get(param_dict)
                else:
                    if PackStream.Rec.bitmap_get is not None:
                        self.value = PackStream.Rec.bitmap_get(param_dict)
            else:
                if PackStream.Rec.value_get is not None:
                    self.value = PackStream.Rec.value_get()

        @staticmethod
        def init_interface(enum_get=None, bitmap_get=None, value_get=None):
            PackStream.Rec.enum_get = enum_get  # With one of param_list, return select value
            PackStream.Rec.bitmap_get = bitmap_get  # With one parameter of param_list, return bitmap value
            PackStream.Rec.value_get = value_get  # With no parameter, return hex or stream value

        def __str__(self):
            if isinstance(self.value, PackStream.Undefined):
                if self.class_type.remark != '':
                    title_str = self.class_type.remark
                else:
                    if hasattr(self.class_type.parameters, '__description__'):
                        title_str = eval(self.class_type.parameters.__name__+'.__description__')
                    else:
                        title_str = self.class_type.parameters.__name__.replace('_', ' ')
                output = '    {:40s}: {}'.format(title_str, str(self.value))
            else:
                output = UnpackStream.param_to_str(UnpackStream.Item(self.class_type.parameters, self.value, len(self.value)), 0)
            return output

    class Undefined:
        def __str__(self):
            return 'Undefined'

    class DataError(Exception):
        pass
