import os
import socket
import threading
from time import ctime
from tkinter import *
from tkinter import filedialog, scrolledtext

HOST = '127.0.0.1' # or 'localhost'
PORT = 8000
BUFFER =1024
ADDR = (HOST,PORT)
PRO_PORT = ''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)

def handle_data(data):
    head,msg = data.split('::')
    if head == 'ONLINE':
        addrs = eval(msg)
        gui.lb.delete(0, 'end')
        if len(addrs) == 0:
            gui.show_msg('\n当前无在线用户...\n', 'fail')
        else:
            gui.show_msg('OK', 'succ')
        for a in addrs:
            gui.lb.insert('end', a)
    elif head == 'MSG':
        gui.show_msg(msg, 'recv')
    elif head == 'FILE':
        gui.show_msg(msg, 'recv')

def recv_data():
    while 1:
        data = s.recv(BUFFER).decode('utf-8')
        if not data:
            break
        handle_data(data)
    s.close()


class ClintWindow(object):
    def __init__(self, root):
        self.__root = root
        self.__root.title('客户端')
        self.__root.resizable(0,0)
        self.show()
        self.sel_list = []
    def show(self):
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

        self.file = Button(self.frm_L_btn, text='文件', command=self.select_file)
        self.file.pack(side=LEFT, anchor=W)
        self.send = Button(self.frm_L_btn, text='发送', command=self.send_msg)
        self.send.pack(side=LEFT, anchor=E, expand=YES)
        self.text_input = Text(self.frm_L, height=12)
        self.text_input.pack(side=TOP, fill=BOTH)

        self.lb = Listbox(self.frm_R, height=12, width=24, selectmode='extended')
        self.lb.pack(side=TOP)
        # for i in range(5):
        #     self.lb.insert('end', i*30)

        self.frm_R_btn = Frame(self.frm_R)
        self.frm_R_btn.pack(side=TOP, fill=BOTH)

        self.sel_btn = Button(self.frm_R_btn, text=' ↓ ', command=self.select_users)
        self.sel_btn.pack(side=LEFT, anchor=W)
        self.del_btn = Button(self.frm_R_btn, text='清空', command=self.empty_users)
        self.del_btn.pack(side=LEFT, anchor=W)
        self.get_list_btn = Button(self.frm_R_btn, text='刷新', command=self.get_online_list)
        self.get_list_btn.pack(side=LEFT, anchor=E, expand=YES)
        self.sel_lb = Listbox(self.frm_R, height=12, width=24)
        self.sel_lb.pack(side=TOP)

    def get_root(self):
        return self.__root

    def get_size(self, filename):
        size = os.path.getsize(filename)
        if pow(2,10)<size<=pow(2,20):
            return f'{size/pow(2,10):.2f} KB'
        elif pow(2,20)<size<=pow(2,30):
            return f'{size/pow(2,20):.2f} MB'
        elif pow(2,30)<size<=pow(2,40):
            return f'{size/pow(2,30):.2f} GB'
        else:
            return f'{size} KB'
    def select_file(self):
        if self.sel_list:
            name = filedialog.askopenfilename()
            size = self.get_size(name)
            info = {'name':name,'size':size}
            if name != '':
                self.text_input.delete(1.0, 'end')
                self.show_msg(f'send file \'{name}\'\nsize: \'{size}\'\n')
                s.send(f'FILE::{info}::{self.sel_list}'.encode())
        else:
            self.show_msg('请选择一个用户...')
    def send_msg(self):
        msg = self.text_input.get(1.0, 'end')
        # print(msg.encode())
        if self.sel_list:
            s.send(f'MSG::{msg}::{self.sel_list}'.encode())
            self.show_msg(msg, 'send')
            self.text_input.delete(1.0, 'end')
        else:
            self.show_msg('请选择一个用户...')
    def select_users(self):
        self.sel_list = [self.lb.get(x) for x in self.lb.curselection()]
        self.sel_lb.delete(0, 'end')
        for usr in self.sel_list:
            self.sel_lb.insert('end', usr)
    def empty_users(self):
        self.sel_lb.delete(0, 'end')
        self.sel_list.clear()
    def get_online_list(self):
        self.show_msg('正在获取在线列表...')
        s.send('ONLINE::::'.encode())
    def show_msg(self, msg, tag=''):
        self.text_show.config(state=NORMAL)
        if tag == 'send':
            self.text_show.insert('end', f'发送...\n[{ctime()}] {msg}', 'send')
        elif tag == 'recv':
            self.text_show.insert('end', f'收到...\n{msg}\n', 'recv')
        elif tag in ['succ', 'fail']:
            self.text_show.insert('end', f'{msg}\n', tag)
        else:
            self.text_show.insert('end', f'[{ctime()}] {msg}', 'send')
        self.text_show.config(state=DISABLED)

def fin():
    gui.get_root().destroy()
    s.close()

def show_gui():
    global gui
    root = Tk()
    gui = ClintWindow(root)
    root.protocol('WM_DELETE_WINDOW', fin)
    root.mainloop()

if __name__ == '__main__':
    t1 = threading.Thread(target=recv_data, args=())
    t2 = threading.Thread(target=show_gui, args=())

    t1.start()
    t2.start()
