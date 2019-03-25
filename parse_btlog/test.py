import parse_protocol


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
param = [0]
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