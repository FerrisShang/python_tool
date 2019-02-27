from struct import unpack
from random import sample
from re import match


class PoemInfo:
    def __init__(self, title_line, content):
        _, t, a = title_line.split('|')
        c_info, c = content.split('|')
        self.title = t.strip()
        self.author = a.strip()
        self.col = int(c_info[1])
        self.row = int(c_info[2])
        self.content = c.strip().split()


class Poem:
    def __init__(self, f_pin='pin.dat', f_poem='poem.dat'):
        fm = open(f_pin, 'rb')
        pin_list = bytes([int(x) ^ 0x5F for x in fm.read(2048)]).decode('utf-8').strip().split()
        self.pin_dict = {}
        self.poem = []
        while True:
            dat = fm.read(4)
            if dat == b'':
                break
            dat = unpack('<I', dat)[0]
            k, p, s = ((dat >> 12) & 0xFFFFF, (dat >> 2) & 0x3FF, dat & 0x03)
            self.pin_dict[k] = [pin_list[p].lower(), s]
        fm.close()

        fp = open(f_poem, 'r', encoding='utf-8')
        line_title = ''
        for line in fp.readlines():
            if line[0] == 'C':
                _poem = PoemInfo(line_title, line)
                self.poem.append(_poem)
            elif line[0] == 'T':
                line_title = line
        fp.close()

    def find_by_last(self, last_py, col_num=0, word_match=True, max_show=20):
        col_num = int(col_num) if isinstance(col_num, str) else col_num
        max_show = int(max_show) if isinstance(max_show, str) else max_show
        word_match = bool(word_match) if isinstance(word_match, str) else word_match
        res = []
        idx = -1
        if last_py[-1] in '0123456789':
            idx = int(last_py[-1]) - 1
            last_py = last_py[:-1]
        for p in self.poem:
            assert(isinstance(p, PoemInfo))
            if col_num == 0 or col_num == p.col:
                for s in p.content:
                    try:
                        poem_last = self.pin_dict[ord(s[-1])]
                        if idx == -1 or idx == poem_last[1]:
                            if word_match and poem_last[0] == last_py:
                                res.append(s)
                            elif poem_last[0][-len(last_py):] == last_py:
                                res.append(s)
                    except KeyError:
                        pass
        if len(res) > max_show:
            return '\n'.join(sample(res, max_show))
        return '\n'.join(res)

    def find_by_con(self, con, col_num=0, max_show=20):
        col_num = int(col_num) if isinstance(col_num, str) else col_num
        max_show = int(max_show) if isinstance(max_show, str) else max_show
        res = []
        for p in self.poem:
            assert(isinstance(p, PoemInfo))
            if col_num == 0 or col_num == p.col:
                for s in p.content:
                    if con in s:
                        res.append([p, s])
        if len(res) > max_show:
            return '\n'.join(sample([s[1] for s in res], max_show))
        elif len(res) == 1:
            return '{}\n{}\n{}'.format(res[0][0].title, res[0][0].author, '\n'.join(res[0][0].content))
        return '\n'.join([s[1] for s in res])

    def find_by_re(self, re, col_num=0, max_show=20):
        col_num = int(col_num) if isinstance(col_num, str) else col_num
        max_show = int(max_show) if isinstance(max_show, str) else max_show
        res = []
        for p in self.poem:
            assert(isinstance(p, PoemInfo))
            if col_num == 0 or col_num == p.col:
                for s in p.content:
                    if match(re, s) is not None:
                        res.append([p, s])
        if len(res) > max_show:
            return '\n'.join(sample([s[1] for s in res], max_show))
        elif len(res) == 1:
            return '{}\n{}\n{}'.format(res[0][0].title, res[0][0].author, '\n'.join(res[0][0].content))
        return '\n'.join([s[1] for s in res])

if __name__ == '__main__':
    poem = Poem()
    while(True):
        try:
            param = input().split()
            if param != []:
                last_param = param
            else:
                param = last_param
            if match('[a-z]+[1-4]?', param[0]):
                print(poem.find_by_last(*param))
            elif sum([1 if ord(x) in poem.pin_dict else 0 for x in param[0]]) == len(param[0]):
                print(poem.find_by_con(*param))
            else:
                print(poem.find_by_re(*param))
        except Exception as e:
            print(e)
