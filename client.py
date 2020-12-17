import os
import socket
import threading
from time import ctime, sleep
from tkinter import (BOTH, DISABLED, END, LEFT, NORMAL, RIGHT, TOP, YES,
                     Button, E, Frame, Listbox, Text, Tk, Toplevel, W, Y,
                     filedialog, messagebox, scrolledtext, ttk)

from PIL import Image, ImageTk, UnidentifiedImageError

import common

HOST = '127.0.0.1' # or 'localhost'
PORT = 8000
BUFFER = 1024
ADDR = (HOST,PORT)
PRO_PORT = ''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)

def handle_data(data: str):
    try:
        data = data.decode('utf-8')
        try:
            head,msg = data.split('::')
        except (TypeError, ValueError) as e:
            print(e)
            print('Transmitting file...')
            data = data.encode()
            head = ''
    except UnicodeDecodeError as e:
        print(e)
        print('Transmitting file...')
        head = ''
    if head == 'ONLINE':
        addrs = eval(msg)
        gui.lb.delete(0, 'end')
        if len(addrs) == 0:
            gui.show('当前无在线用户...\n', 'fail')
        else:
            gui.show('OK\n', 'succ')
            for a in addrs:
                gui.lb.insert('end', a)
            gui.lb.select_set(0, END)
    elif head == 'MSG':
        gui.show(f'{msg}\n', 'recv')
    elif head == 'FILE':
        if msg == 'OK':
            with open(gui.filename, 'rb') as f:
                for data in f:
                    s.send(data)
        else:
            data, addr = msg.split(';;')
            info = eval(data)
            name = info['name']
            size = info['size']
            msg = f'是否接收来自{addr}的文件\n{name} {size}'
            mb_file = messagebox.askokcancel(title='收到文件...', message=msg)
            if mb_file:
                gui.send(f'FILE::OK::{addr}')
                common.chdir2desktop()
                gui.filename = name
                gui.filesize = size
                # t3 = threading.Thread(target=show_pro_bar, args=())
                # t3.start()
                show_pro_bar()
            else:
                pass
    elif head == 'IMG':
        data, addr = msg.split(';;')
        info = eval(data)
        gui.filename = info['name']
        gui.filesize = info['size']
        common.chdir2desktop()
        if os.path.exists(gui.filename):
            os.remove(gui.filename)
    else:
        with open(gui.filename, 'ab') as f:
            f.write(data)
        if gui.filename.endswith(('jpg','png','jpeg','bmp','gif')):
            try:
                if len(data) < 1024:
                    sleep(0.5)
                    gui.show(gui.filename, 'img')
                    print(gui.filename)
            except (UnidentifiedImageError, OSError) as e:
                print(e)
        else:
            pro_bar.update(BUFFER, gui.filesize)

def show_pro_bar():
    global pro_bar
    top = Toplevel()
    pro_bar = common.ProgressbarWindow(top)

def recv_data():
    while 1:
        data = s.recv(BUFFER)
        if not data:
            break
        handle_data(data)
    s.close()


class ClientWindow(object):
    def __init__(self, root):
        self.__root = root
        self.__root.title('客户端')
        self.__root.resizable(0,0)
        self.draw()
        self.sel_list = []
        self.img_dict = {}
        self.filename = ''
        self.filesize = 0 #字节
    def draw(self):
        self.frm = Frame(self.__root)
        self.frm.pack(fill=Y)

        self.frm_L = Frame(self.frm)
        self.frm_L.pack(side=LEFT, fill=BOTH)
        self.frm_R = Frame(self.frm)
        self.frm_R.pack(side=RIGHT, fill=BOTH)

        self.text_show = scrolledtext.ScrolledText(self.frm_L, font=('', 14), state=DISABLED, height=21)
        self.text_show.pack(side=TOP)
        self.text_show.tag_config('succ', foreground='green')
        self.text_show.tag_config('fail', foreground='red')
        self.text_show.tag_config('send', foreground='blue')
        self.text_show.tag_config('recv', foreground='orangered')

        self.frm_L_btn = Frame(self.frm_L)
        self.frm_L_btn.pack(side=TOP, fill=BOTH)

        self.btn_file = Button(self.frm_L_btn, text='文件', command=self.select_file)
        self.btn_file.pack(side=LEFT, anchor=W, expand=YES)
        self.btn_clear = Button(self.frm_L_btn, text='清屏', command=self.clear)
        self.btn_clear.pack(side=LEFT, anchor=E)
        self.btn_send = Button(self.frm_L_btn, text='发送', command=self.send_msg)
        self.btn_send.pack(side=LEFT, anchor=E)
        self.text_input = Text(self.frm_L, height=12)
        self.text_input.pack(side=TOP, fill=BOTH)

        self.lb = Listbox(self.frm_R, height=12, width=24, selectmode='extended')
        self.lb.pack(side=TOP)
        # for i in range(5):
        #     self.lb.insert('end', i*30)

        self.frm_R_btn = Frame(self.frm_R)
        self.frm_R_btn.pack(side=TOP, fill=BOTH)

        self.btn_sel = Button(self.frm_R_btn, text=' ↓ ', command=self.select_users)
        self.btn_sel.pack(side=LEFT, anchor=W)
        self.btn_del = Button(self.frm_R_btn, text='清空', command=self.empty_users)
        self.btn_del.pack(side=LEFT, anchor=W)
        self.btn_get_list = Button(self.frm_R_btn, text='刷新', command=self.get_online_list)
        self.btn_get_list.pack(side=LEFT, anchor=E, expand=YES)
        self.lb_sel = Listbox(self.frm_R, height=12, width=24)
        self.lb_sel.pack(side=TOP)

    def get_root(self):
        return self.__root

    def select_file(self):
        self.filename = filedialog.askopenfilename()
        if self.filename == '':
            return
        if self.sel_list:
            name = self.filename
            size = common.get_size(name)
            self.filesize = os.path.getsize(name)
            info = {'name':os.path.basename(name),'size':self.filesize}
            self.show(f'send file \'{name}\'\nsize: \'{size}\'\n')
            if name.endswith(('jpg','png','jpeg','bmp','gif')):
                self.show(name, 'img')
                self.send(f'IMG::{info}::{self.sel_list}')
                with open(self.filename, 'rb') as f:
                    for data in f:
                        s.send(data)
            elif name != '':
                # self.text_input.delete(1.0, 'end')
                self.send(f'FILE::{info}::{self.sel_list}')
        else:
            self.show('请至少选择一个用户...\n')
    def clear(self):
        self.img_dict.clear()
        self.text_show.config(state=NORMAL)
        self.text_show.delete(1.0, 'end')
        self.text_show.config(state=DISABLED)
    def send_msg(self):
        msg = self.text_input.get(1.0, 'end')
        if self.sel_list:
            self.send(f'MSG::{msg}::{self.sel_list}')
            self.show(f'{msg}\n')
            self.text_input.delete(1.0, 'end')
        else:
            self.show('请至少选择一个用户...\n')
    def send(self, msg: str):
        """对socket.send()方法的封装

        Args:
            msg (str): 需要发送的字符串
        """
        s.send(msg.encode())

    def select_users(self):
        self.sel_list = [self.lb.get(x) for x in self.lb.curselection()]
        self.lb_sel.delete(0, 'end')
        for usr in self.sel_list:
            self.lb_sel.insert('end', usr)
    def empty_users(self):
        self.lb_sel.delete(0, 'end')
        self.sel_list.clear()
    def get_online_list(self):
        self.show('正在获取在线列表...\n')
        self.send('ONLINE::::')

    def show(self, msg: str, tag=''):
        """显示接收或发送的文字消息

        Args:
            msg (str): 需要显示的文字
            tag (str, optional): 文字标识（颜色、背景、字体等）. Defaults to ''.
        """
        self.text_show.config(state=NORMAL)
        # if tag != 'img':
        self.text_show.insert('end', f'[{ctime()}] ', 'send')
        if tag == 'recv':
            self.text_show.insert('end', f'{msg}', 'recv')
        elif tag in ['succ', 'fail']:
            self.text_show.insert('end', f'{msg}', tag)
        elif tag == 'img':
            self.text_show.insert('end', '\n', 'send')
            photo = ImageTk.PhotoImage(Image.open(msg))
            self.img_dict[ctime()] = photo
            self.text_show.image_create(END, image=photo)
            self.text_show.insert('end', '\n', 'send')
        elif tag == '\n':
            self.text_show.insert('end', '\n', 'send')
        else:
            self.text_show.insert('end', f'{msg}', 'send')
        self.text_show.config(state=DISABLED)

def fin():
    gui.get_root().destroy()
    s.close()

def show_gui():
    global gui
    root = Tk()
    gui = ClientWindow(root)
    root.protocol('WM_DELETE_WINDOW', fin)
    root.mainloop()

if __name__ == '__main__':
    t1 = threading.Thread(target=recv_data, args=())
    t2 = threading.Thread(target=show_gui, args=())

    t1.start()
    t2.start()
