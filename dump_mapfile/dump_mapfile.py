import sys


def get_size(filename, sector):
    f = open(filename, 'r')
    parse_flag = False
    lines = f.readlines()
    idx = -1
    output = []
    while idx < len(lines)-1:
        idx += 1
        line_raw = lines[idx]
        line = line_raw.strip()
        if not parse_flag and len(line)>=len(sector) and sector == line[:len(sector)]:
            print(line)
            parse_flag = True
            continue
        if parse_flag:
            if len(line) == 0:
                break
            if False:
                items = line.split()
                if len(items) < 3 or items[2].strip() != '0x0':
                    output.append(line)
                    continue
            else:
                if len(line) < 2 or line[:2] == '0x' or line_raw[0] != ' ':
                    continue
                items = line.split()
                if len(items) > 0 and items[0] == '*fill*':
                    output.append(line)
                    continue
                if len(items) == 1 and lines[idx+1].strip()[:2] == '0x':
                    line = (('{:20s}'.format(line) if len(line)<21 else (line[:9]+'..'+line[-9:]))+' '+lines[idx+1].strip()).strip()
                    items = line.split()
                if len(items) == 4:
                    try:
                        size = int(items[2], 0)
                        if size > 0:
                            if len(line) > 100:
                                output.append(line[:60] + '***' + line[-37:])
                            else:
                                output.append(line)
                    except:
                        raise
                        pass
                    continue
    output.sort(key=lambda x:int(x.split()[2], 0), reverse=True)
    for p in output:
        print(p)
    f.close()

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        for _ in range(2, len(sys.argv)):
            get_size(sys.argv[1], sys.argv[_])
            print('')

