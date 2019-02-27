import curses
import time, os
from curses import panel
import pyperclip
from platform import system as system_name


class Window:
    def __init__(self, x, y, width, height, title=None, hide=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.window = curses.newwin(height, width, y, x)
        self.window.border('|', '|', '-', '-', '*', '*', '*', '*')
        if title is not None:
            if Window.console_width(title) < self.width - 5:
                self.window.addstr(0, 2, ' ' + title + ' ')
            else:
                self.window.addstr(0, 0, title[:self.width-3]+'...')
        self.panel = panel.new_panel(self.window)

        if hide:
            self.panel.hide()

        self.update()

    def hide(self):
        self.panel.hide()

    def show(self):
        self.panel.show()

    def update(self):
        self.panel.top()
        self.window.refresh()
        GUI.update_panels(panel)

    @staticmethod
    def console_width(string):
        return sum([1 if 1 <= ord(x) <= 255 else 2 for x in string])


class BasicList(Window):
    def __init__(self, x, y, width=None, height=None, title=None, hide=False, items=None):
        """
        :param x: pos x
        :param y: pox y
        :param width: window width
        :param height: window height
        :param title: title of window
        :param hide: is window hide
        :param items: items list or callback for get items data:
                        [list, selected_idx] (*callback) (start_idx, items_num, search_str)
                            -> IN: [None, None, None] OUT: [items_num, items_width]
                            -> IN: [None, None, search_str] OUT: [list, selected_idx]
                            -> IN: [start_idx, items_num, None] OUT: [list, None]
        """
        assert(items is not None and height is not None)
        assert(height > 2)

        self.item_pos = 2
        self.item_top_pos = 1
        self.item_show_max = height - 2
        if isinstance(items, list):
            self.item_width = max([self.console_width(x) for x in items]) if len(items) > 0 else 10
            self.items_num = len(items)
        else:
            self.items_num, self.item_width = items[0](None, None, None, items[1])
        width = max(0 if width is None else width, 4 + self.item_width)
        Window.__init__(self, x, y, width, height, title, hide)
        self.top_idx = 0
        if isinstance(items, list):
            self.items = items
            self.items_cb = None
        else:
            self.items_cb = items[0]
            self.items_cb_param = items[1]
        self.show_data(self.top_idx)

    def show_data(self, top_idx, high_light_idx=None):
        if top_idx > self.items_num - self.item_show_max:
            top_idx = max(0, self.items_num - self.item_show_max)

        if self.items_cb is None:
            items_data = self.items[top_idx:top_idx+min(self.items_num, self.item_show_max)]
        else:
            items_data = self.items_cb(top_idx, min(self.items_num, self.item_show_max), None, self.items_cb_param)[0]

        for i in range(len(items_data)):
            attr = curses.A_REVERSE if high_light_idx == top_idx+i else 0
            self.window.addstr(self.item_top_pos + i, self.item_pos,
                               '{}{}'.format(
                                   items_data[i] if self.item_width >= Window.console_width(items_data[i])
                                   else items_data[i][:self.item_width-1] + '~',
                                   ' ' * (self.item_width - Window.console_width(items_data[i]))
                               ), attr)
        self.top_idx = top_idx
        return top_idx


class SelectList(BasicList):
    def __init__(self, x, y, width=None, height=None, title=None, hide=False, items=None, selected_idx=None):
        assert(items is not None and height is not None and selected_idx is not None)
        assert(height > 2)
        BasicList.__init__(self, x, y, width, height, title, hide, items)
        self.reserve_space = 3
        self.scroll_idx = None
        self.selected = 0
        self.set_selected(selected_idx)

    def set_selected(self, selected_idx):
        assert(0 <= selected_idx < self.items_num)
        if self.selected < selected_idx:  # down
            cus_to_end = self.item_show_max - (self.selected - self.top_idx) - \
                         max(self.reserve_space, min(0, self.items_num - self.top_idx - self.item_show_max))
            self.top_idx = self.top_idx + max(0, (selected_idx - self.selected) - cus_to_end)
        elif self.selected > selected_idx:  # up
            cus_to_start = (self.selected - self.top_idx) - \
                           (0 if self.top_idx == 0 else self.reserve_space - 1)
            self.top_idx = max(0, self.top_idx + min(0, cus_to_start - (self.selected - selected_idx)))
        self.show_data(self.top_idx, selected_idx)
        self.selected = selected_idx
        self.show_scroll(selected_idx)
        self.update()

    def show_scroll(self, selected_idx):
        if self.scroll_idx is not None:
            self.window.addstr(self.scroll_idx, self.width - 1, '|')
        if self.items_num > self.item_show_max:
            idx = round(selected_idx / self.items_num * self.item_show_max)
            self.scroll_idx = max(1, idx)
            self.window.addstr(self.scroll_idx, self.width - 1, '$')
        else:
            self.scroll_idx = None

    def choose(self):
        now = time.time()
        search_str = ''
        while True:
            self.update()
            ch = self.window.getch()
            idx = self.selected
            if ch == ord('/') or ch == ord('?'):  # exit
                return -1
            elif ch == ord(','):  # up
                idx = max(idx - 1, 0)
            elif ch == ord('.'):  # down
                idx = min(idx + 1, self.items_num-1)
            elif ch == ord('<'):  # scroll up
                idx = max(idx - max(1, self.item_show_max - self.reserve_space*2), 0)
            elif ch == ord('>'):  # scroll down
                idx = min(idx + max(1, self.item_show_max - self.reserve_space*2), self.items_num-1)
            elif ch == 10:  # entry
                return idx
            elif ord('0') <= ch <= ord('9') or ord('a') <= ch <= ord('Z') or ord('a') <= ch <= ord('z'):
                search_str = chr(ch) if time.time() > now + 1 else search_str + chr(ch)
                if self.items_cb is None:
                    for i in range(self.items_num):
                        if search_str in self.items[i]:
                            idx = i
                            break
                else:
                    idx = self.items_cb(None, None, search_str, self.items_cb_param)[1]
                now = time.time()
            self.set_selected(idx)


class GUI:
    def __init__(self):
        self.screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        self.screen.keypad(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)

        self.windows = {}

    def add_state_box(self):
        pass

    def test(self):
        self.screen.getch()
        self.screen.addstr(str(curses.curs_set(1)))
        self.screen.refresh()
        try:
            # self.screen.box()
            box1 = curses.newwin(10, 20, 5, 10)
            box1.box()
            box1.addstr(5, 7, 'xxxxxx')
            box2 = curses.newwin(10, 20, 8, 16)
            box2.addstr(5, 7, '{} {}'.format(*self.screen.getmaxyx()))
            box2.box()

            box1.refresh()
            box2.refresh()

            box1.border('|', '|', '-', '-', '*', '*', '*', '*')
            box2.border('|', '|', '-', '-', '*', '*', '*', '*')
            # for i in range(1, 9):
            #     box2.addstr(i,0, '*')
            #     box2.addstr(i,18, '*')

            b1 = panel.new_panel(box1)
            b2 = panel.new_panel(box2)
            box1.refresh()
            box2.refresh()

            b1.top()
            box1.refresh()
            # panel.update_panels()
            self.screen.getch()
            b2.top()
            box2.refresh()
            # panel.update_panels()
            self.screen.getch()
            b1.top()
            box1.refresh()
            # panel.update_panels()
            self.screen.getch()
            box1.clear()
            box1.refresh()
            self.screen.getch()
            x = box1.timeout(-1)
            pos = 3
            while True:
                x = box1.getch()
                if x == -1:
                    x = pyperclip.paste()
                    pass
                else:
                    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
                    # box1.addstr(5, 7, '{}'.format(x))
                    pos = 3+((pos+1)%5)
                    box1.addstr(pos, 7, '{}'.format(x),
                                + curses.color_pair(1)
                                + curses.A_UNDERLINE
                                # + curses.A_BLINK # windows seems not support
                                + curses.A_BOLD
                                + curses.A_REVERSE
                                )
                    box2.refresh()
                # time.sleep(1)

        finally:
            curses.endwin()

    def create_window(self, x, y, width, height, title=None, hide=False, win_id=None):
        assert(win_id is not None)
        win = Window(x, y, width, height, title, hide)
        if win_id is not None:
            if win_id in self.windows:
                raise self.Error('Invalid win_id, already exist.')
            self.windows[win_id] = win
        return win

    def create_basic_list(self, x, y, width=None, height=None, title=None, hide=False, items=None, win_id=None):
        assert(win_id is not None)
        win = BasicList(x, y, width, height, title, hide, items)
        if win_id is not None:
            if win_id in self.windows:
                raise self.Error('Invalid win_id, already exist.')
            self.windows[win_id] = win
        return win

    @staticmethod
    def create_select_list(x, y, width=None, height=None, title=None, hide=False, items=None, selected_idx=0):
        win = SelectList(x, y, width, height, title, hide, items, selected_idx)
        return win

    @staticmethod
    def input_box(x, y, width_limit=8, title=None, hide=False, ret_type=str, check_cb=None):
        win = Window(x, y, width_limit + 4, 3, title, hide)
        curses.curs_set(2)
        curses.echo()
        while True:
            win.window.addstr(1, 2, ' ' * width_limit)
            input_str = win.window.getstr(1, 2, width_limit)
            try:
                ret_type(input_str)
            except ValueError:
                continue
            if check_cb is None or check_cb(input_str):
                break
        curses.noecho()
        curses.curs_set(0)
        return ret_type(input_str)

    @staticmethod
    def update_panels(p):
        if system_name().lower() != "windows":
            p.update_panels()

    class Error(Exception):
        pass


def items_callback(start_idx, items_num, search_str, param):
    """
        -> IN: [None, None, None, param] OUT: [items_num, items_width]
        -> IN: [None, None, search_str, param] OUT: [None, selected_idx]
        -> IN: [start_idx, items_num, None, param] OUT: [list, None]
    """
    if start_idx is None and items_num is None and search_str is None:
        return 100, 20
    elif start_idx == items_num is None and isinstance(search_str, str):
        pass
    else:
        return [str(x) + ' | ' + str(x/17) for x in range(start_idx, start_idx+items_num)], None

    return


if __name__ == '__main__':
    gui = GUI()
    try:
        gui.input_box(1, 1)
        t_list = gui.create_select_list(40, 5, None, 8+2, title='title123123123',
                               # items=items_callback,
                               items=[str(x) + ' | ' + str(x/17) for x in range(80)],
                               selected_idx=0,
                        )
        t_list.show_data(0)
        b_list = gui.create_select_list(0, 5, None, 16, title='title123123123',
                               items=(items_callback, None),
                               # items=[str(x) + ' | ' + str(x/17) for x in range(40)],
                               selected_idx=0,
                        )
        b_list.choose()
        gui.screen.getch()
    finally:
        curses.endwin()
