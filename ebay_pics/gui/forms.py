import os
import logging
from collections import OrderedDict
import tkinter as tk
import tkinter.filedialog as filedialog
import ebay_pics.settings as env


logger = logging.getLogger(__name__)
FORM_FONT = '-family {Segoe UI} -size 14 -weight normal -slant ' \
            'roman -underline 0 -overstrike 0'
INFO_FONT = FORM_FONT.replace('14', '10')


class ButtonFrame(tk.Frame):
    def __init__(self, root):
        logger.debug('Creating ButtonFrame')
        tk.Frame.__init__(self, root)
        self.root = root
        self.page_link = tk.StringVar()
        self.item_num = tk.StringVar()
        self.files = None

    def _create_frame(self):
        self.place(x=5, y=5, height=140, width=790)
        self.configure(relief=tk.GROOVE)
        self.configure(borderwidth='2')
        self.configure(relief=tk.GROOVE)
        self.configure(background='#d9d9d9')
        logger.debug('Create frame for main buttons')

    def _create_file_entry(self):
        self.file_entry = tk.Entry(self)
        self.file_entry.place(x=10, y=40, height=30, width=395)
        self.file_entry.configure(background='white')
        self.file_entry.configure(disabledforeground='#a3a3a3')
        self.file_entry.configure(font='TkFixedFont')
        self.file_entry.configure(foreground='#000000')
        self.file_entry.configure(insertbackground='black')
        self.file_entry.configure(textvariable=self.page_link)
        logger.debug('Create file path entry')

    def _create_num_entry(self):
        self.num_entry = tk.Entry(self)
        self.num_entry.place(x=600, y=40, height=30, relwidth=0.13)
        self.num_entry.configure(background='white')
        self.num_entry.configure(disabledforeground='#a3a3a3')
        self.num_entry.configure(font='TkFixedFont')
        self.num_entry.configure(foreground='#000000')
        self.num_entry.configure(highlightbackground='#d9d9d9')
        self.num_entry.configure(highlightcolor='black')
        self.num_entry.configure(insertbackground='black')
        self.num_entry.configure(selectbackground='#c4c4c4')
        self.num_entry.configure(selectforeground='black')
        self.num_entry.configure(width=115)
        self.num_entry.configure(font=FORM_FONT)
        self.num_entry.configure(textvariable=self.item_num)
        logger.debug('Create entry field for number of lots')
        self.item_num.set('200')
        logger.debug('Set default number of lots to 200')

    def _create_file_btn(self):
        self.btn_file = tk.Button(self)
        self.btn_file.place(relx=0.01, rely=0.64, height=40, width=395)
        self.btn_file.configure(activebackground='#d9d9d9')
        self.btn_file.configure(activeforeground='#000000')
        self.btn_file.configure(background='#d9d9d9')
        self.btn_file.configure(disabledforeground='#a3a3a3')
        self.btn_file.configure(font=FORM_FONT)
        self.btn_file.configure(foreground='#000000')
        self.btn_file.configure(highlightbackground='#d9d9d9')
        self.btn_file.configure(highlightcolor='black')
        self.btn_file.configure(pady='0')
        self.btn_file.configure(text='Указать файлы лотов')
        self.btn_file.configure(width=387)
        logger.debug('Create file path button')

    def _create_start_bnt(self):
        self.start_btn = tk.Button(self)
        self.start_btn.place(relx=0.71, rely=0.57, height=50, width=155)
        self.start_btn.configure(activebackground='#d9d9d9')
        self.start_btn.configure(activeforeground='#000000')
        self.start_btn.configure(background='#d9d9d9')
        self.start_btn.configure(disabledforeground='#a3a3a3')
        self.start_btn.configure(font=FORM_FONT)
        self.start_btn.configure(foreground='#000000')
        self.start_btn.configure(highlightbackground='#d9d9d9')
        self.start_btn.configure(highlightcolor='black')
        self.start_btn.configure(pady='0')
        self.start_btn.configure(text='Скачать')
        logger.debug('Configured download button')

    def _create_labels(self):
        file_label = tk.Label(self)
        file_label.place(relx=0.1, rely=0.04, height=31, width=280)
        file_label.configure(background='#d9d9d9')
        file_label.configure(disabledforeground='#a3a3a3')
        file_label.configure(font=FORM_FONT)
        file_label.configure(foreground='#000000')
        file_label.configure(text='Ссылка на список/Путь к файлу')

        down_label = tk.Label(self)
        down_label.place(relx=0.58, rely=0.04, height=31, width=257)
        down_label.configure(background='#d9d9d9')
        down_label.configure(disabledforeground='#a3a3a3')
        down_label.configure(font=FORM_FONT)
        down_label.configure(foreground='#000000')
        down_label.configure(text='Число лотов для скачивания')
        logger.debug('Configured lots\' number label')

    def start(self):
        self._create_frame()
        self._create_file_entry()
        self._create_num_entry()
        self._create_file_btn()
        self._create_start_bnt()
        self._create_labels()
        logger.debug('Successfully finished ButtonFrame creation')
        return self

    def assign_file_callback(self, func):
        self.btn_file.configure(command=lambda: self._file_callback(func))
        logger.info('Assigned function callback to find files button')

    def assign_start_callback(self, func):
        self.start_btn.configure(command=func)
        logger.info('Assigned function callback to start download button')

    def _file_callback(self, func):
        try:
            cur_dir = env.BASE_DIR
            logger.info('Assigned {} to active directory'.format(cur_dir))
        except AttributeError:
            cur_dir = os.path.dirname(__file__)
            logger.info('Set active directory to program directory')
        self.files = [self.page_link.get()] if self.page_link.get() != '' else list()
        self.files.extend(filedialog.askopenfilenames(initialdir=cur_dir))
        func()
        if len(self.files) > 0:
            self.page_link.set(self.files[0])


class ItemsFrame(tk.Frame):
    def __init__(self, root, name, path):
        tk.Frame.__init__(self, root)
        logger.debug('Creating ItemsFrame instance')
        self.name = name
        self.height = 80
        self.width = 750
        self.done = False
        self.started = False
        self.path = path
        
    def _create_frame(self, xpos, ypos):
        self.place(x=xpos, y=ypos, height=self.height, width=self.width)
        self.configure(relief=tk.GROOVE)
        self.configure(borderwidth='2')
        self.configure(relief=tk.GROOVE)
        self.configure(background='#d9d9d9')
        logger.debug('Created frame with X {} Y {}'.format(xpos, ypos))

    def _create_info_frame(self):
        self._lframe = tk.Frame(self)
        self._lframe.pack(side=tk.LEFT)
        self._sframe = ItemInfo(self)
        self._sframe.pack(side=tk.RIGHT)
        logger.debug('Created info frame')

    def set_inactive(self):
        self._sframe.set_inactive()
        logger.info('Set frame {} to inactive'.format(self.name))

    def set_active(self, total_lots):
        self.started = True
        self._sframe.set_active(total_lots)
        logger.info('Set frame {} to active'.format(self.name))

    def add_one_done(self):
        self._sframe.add_one_done()

    def set_done(self):
        self.done = True
        self._sframe.set_done()
        logger.info('Set frame {} to done'.format(self.name))

    def _create_label(self):
        items_label = tk.Label(self._lframe)
        items_label.configure(background='#d9d9d9')
        items_label.configure(disabledforeground='#a3a3a3')
        items_label.configure(font=FORM_FONT)
        items_label.configure(foreground='#000000')
        items_label.configure(text=self.name)
        items_label.pack(expand=tk.YES, fill=tk.BOTH, anchor=tk.NW)
        logger.debug('Create named label for frame {}'.format(self.name))

    def start(self, xpos, ypos):
        self._create_frame(xpos, ypos)
        self._create_info_frame()
        self._create_label()
        self.set_inactive()
        self.pack(expand=tk.YES, fill=tk.BOTH)
        logger.debug('Finally created ItemsFrame {}'.format(self.name))
        return self


class ItemInfo(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        logger.debug('Creating Info panel for object {}'.format(root.name))
        self._name = root.name
        self._status_label = tk.Label(self)
        self._total_label = tk.Label(self)
        self._got_label = tk.Label(self)
        self._total = None
        self._got = None

    @staticmethod
    def _configure_label(label_obj, color, label_text, anchor):
        label_obj.configure(background=color, disabledforeground='#a3a3a3',
                            foreground='#000000', font=INFO_FONT, text=label_text)
        label_obj.pack(expand=tk.YES, fill=tk.BOTH, anchor=anchor)

    def set_inactive(self):
        self._configure_label(self._status_label, 'RED', 'В очереди', tk.NE)
        self._configure_label(self._total_label, '#d9d9d9',
                              'Общее число лотов: {}'.format(self._total), tk.NE)
        self._configure_label(self._got_label, '#d9d9d9',
                              'Обработано лотов: {}'.format(self._got), tk.SE)

    def set_active(self, total_lots=None):
        self._total = total_lots
        self._got = 0
        self._status_label.configure(background='YELLOW')
        self._status_label.configure(text='Скачивается')
        self._total_label.configure(text='Общее число лотов: {}'.format(self._total))
        self._got_label.configure(text='Обработано лотов: {}'.format(self._got))

    def add_one_done(self):
        self._got += 1
        self._got_label.configure(text='Обработано лотов: {}'.format(self._got))

    def set_done(self):
        self._status_label.configure(background='GREEN')
        self._status_label.configure(text='Загружено')


class ItemsList(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        logger.debug('Creating ItemsList instance')
        self._root = root
        self._curx = 5
        self._cury = 5
        self._position = 0
        self.items = dict()
        self._windows = OrderedDict()

    def _config_list(self):
        self.place(x=5, y=150, height=580, width=790)
        self.configure(relief=tk.GROOVE)
        self.configure(borderwidth='2')
        self.configure(relief=tk.GROOVE)
        self.configure(background='#d9d9d9')
        logger.debug('Configured ItemsList')

    def _create_canvas(self):
        self.canvas = tk.Canvas(self)
        self.canvas.place(x=5, y=5, height=630, width=780)
        self.canvas.configure(borderwidth='2')
        self.canvas.configure(background='#d9d9d9')
        logger.debug('Configured canvas for ItemsList')

    def _create_scroll(self):
        self.sbar = tk.Scrollbar(self)
        self.canvas.config(yscrollcommand=self.sbar.set)
        self.canvas.config(scrollregion=(0, 0, 0, 0))
        self.sbar.config(command=self.canvas.yview)
        self.sbar.pack(side=tk.RIGHT, fill=tk.Y)
        logger.debug('Configured Scrollbar for ItemsList')

    def add_list(self, name, path):
        frame = ItemsFrame(self.canvas, name, path).start(self._curx, self._cury)
        window = self.canvas.create_window(0, self._position, anchor=tk.NW, window=frame,
                                           width=frame.width, height=frame.height)
        prev_pos = self._position
        self._position += frame.height + 10
        self._cury += frame.height + 10
        self.canvas.config(scrollregion=(0, 0, 0, self._position))
        self.items[path] = frame
        self._windows[path] = [window, prev_pos]
        logger.info('Added ItemFrame {} to the list'.format(path))

    def remove_list(self, path):
        del self.items[path]
        logger.debug('Removed ItemFrame {} from the list'.format(path))
        self.canvas.delete(self._windows[path][0])
        self._redraw_lists(self._windows.pop(path)[1])

    def _redraw_lists(self, position):
        for key in self._windows.keys():
            if self._windows[key][1] > position:
                logger.debug('Switching position for {}: '
                             'from {} to {}'.format(key, self._windows[key][1], position))
                self._windows[key][1], position = position, self._windows[key][1]
                self.canvas.move(self._windows[key][0],
                                 0, self._windows[key][1] - position)
        if len(self._windows.keys()) > 0:
            self._position = self._windows[list(self._windows.keys())[-1]][1]
            logger.debug('Set position attribute to {}'.format(self._position))
        else:
            logger.debug('Set position to 0')
            self._position = 0

    def start(self):
        self._config_list()
        self._create_canvas()
        self._create_scroll()
        logger.debug('Started ItemList')
        return self


class ClearButton(tk.Button):
    def __init__(self, root):
        tk.Button.__init__(self, root)
        self._root = root
        logger.debug('Creating ClearButton instance')

    def start(self):
        self.place(x=5, y=740, height=50, width=790)
        self.configure(activebackground='#d9d9d9')
        self.configure(activeforeground='#000000')
        self.configure(background='#d9d9d9')
        self.configure(disabledforeground='#a3a3a3')
        self.configure(font=FORM_FONT)
        self.configure(foreground='#000000')
        self.configure(highlightbackground='#d9d9d9')
        self.configure(highlightcolor='black')
        self.configure(pady='0')
        self.configure(text='Очистить список')
        logger.info('Created ClearButton instance')
        return self

    def assign_callback(self, func):
        logger.info('Assigned callback for ClearButton')
        self.configure(command=func)
