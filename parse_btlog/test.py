import parse_protocol


if __name__ == '__main__':
    print('')
    parse_protocol.UnpackStream(b'\x04\x0e\x04\x01\x0c\x20\x00').dump()
    print('')
    parse_protocol.UnpackStream(b'\x02\x40\x20\x0b\x00\x11\x00\x06\x00\x0E\x03\x00\x01\x10\x02\x03\x02\x04\x03').dump()

    def enum_get(param_dict):
        for k, v in param_dict.items():
            print(k, v)
        _ = int(input())
        return _

    def bitmap_get(param_dict):
        for k, v in param_dict.items():
            print(k, v)
        _ = int(input())
        return _

    def value_get():
        return int(input(), 0)

    parse_protocol.PackStream.Rec.init_interface(enum_get, bitmap_get, value_get)
    param = [1]
    while True:
        x = parse_protocol.PackStream(*param)
        # x.dump_rec()
        rs = x.get_rec_list()
        for i, r in enumerate(rs):
            print(i + 1, str(r))
        idx = int(input())
        rs[idx - 1].input()
        param = x.to_input_arg()
        stream = x.to_stream()
        if stream is not None:
            print(parse_protocol.UnpackStream(stream).to_string())
