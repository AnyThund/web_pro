import os
import socket
import threading
from tkinter import *
from tkinter import filedialog, scrolledtext
from time import ctime
from PIL import Image, ImageTk

import common

HOST = '127.0.0.1' # or 'localhost'
PORT = 8000
BUFFER =1024
ADDR = (HOST,PORT)
PRO_PORT = ''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)

def handle_data(data):
    head,msg, = data.split('::')
    if head == 'ONLINE':
        addrs = eval(msg)
        gui.lb.delete(0, 'end')
        if len(addrs) == 0:
            gui.show('\n当前无在线用户...\n', 'fail')
        else:
            gui.show('OK', 'succ')
            for a in addrs:
                gui.lb.insert('end', a)
            gui.lb.select_set(0, END)
    elif head == 'MSG':
        gui.show(msg, 'recv')
    elif head == 'FILE':
        gui.show(msg, 'recv')
    elif head == 'IMG':
        gui.show(msg, 'recv')

def recv_data():
    while 1:
        data = s.recv(BUFFER).decode('utf-8')
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
        self.btn_file.pack(side=LEFT, anchor=W)
        self.btn_send = Button(self.frm_L_btn, text='发送', command=self.send_msg)
        self.btn_send.pack(side=LEFT, anchor=E, expand=YES)
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
        if self.sel_list:
            name = filedialog.askopenfilename()
            print(name, type(name))
            size = common.get_size(name)
            info = {'name':os.path.basename(name),'size':size}
            if name != '':
                if name.endswith(('jpg','png','jpeg','bmp','gif')):
                    print('tupian')
                    self.show(f'send file \'{name}\'\nsize: \'{size}\'\n')
                    self.show(name, 'file')
                else:
                    # self.text_input.delete(1.0, 'end')
                    self.show(f'send file \'{name}\'\nsize: \'{size}\'\n')
                    self.send(f'FILE::{info}::{self.sel_list}')
        else:
            self.show('请至少选择一个用户...')
    def send_msg(self):
        msg = self.text_input.get(1.0, 'end')
        if self.sel_list:
            self.send(f'MSG::{msg}::{self.sel_list}')
            self.show(msg, 'send')
            self.text_input.delete(1.0, 'end')
        else:
            self.show('请至少选择一个用户...')
    def send(self, msg: str):
        """对socket.send()方法的封装

        Args:
            msg (str): 需要发送的字符串
        """
        head,data,usrs = msg.split('::')
        if head == 'FILE':
            pass
        elif head == 'IMG':
            pass
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
        self.show('正在获取在线列表...')
        self.send('ONLINE::::')

    def show(self, msg: str, tag=''):
        """显示接收或发送的文字消息

        Args:
            msg (str): 需要显示的文字
            tag (str, optional): 文字标识（颜色、背景、字体等）. Defaults to ''.
        """
        self.text_show.config(state=NORMAL)
        self.text_show.insert('end', f'[{ctime()}] ', 'send')
        if tag == 'send':
            self.text_show.insert('end', f'[{ctime()}] {msg}', 'send')
        elif tag == 'recv':
            self.text_show.insert('end', f'{msg}\n', 'recv')
        elif tag in ['succ', 'fail']:
            self.text_show.insert('end', f'{msg}\n', tag)
        elif tag == 'file':
            photo = ImageTk.PhotoImage(Image.open(msg))
            self.img_dict[ctime()] = photo
            self.text_show.image_create(END, image=photo)
        elif tag == '\n':
            self.text_show.insert('end', '\n', 'send')
        else:
            self.text_show.insert('end', f'[{ctime()}] {msg}', 'send')
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
