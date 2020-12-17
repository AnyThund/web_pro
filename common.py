"""一些公用的函数库
"""

import os
from tkinter import ttk, Toplevel, Label

def get_size(filename: str) -> str:
    """将os.path.getsize()得到的字节数，转化为易读的表示\n
    例如：输出'2 KB'

    Args:
        filename (str): 文件路径

    Returns:
        str: 文件大小
    """
    size = os.path.getsize(filename)
    if pow(2,10)<size<=pow(2,20):
        return f'{size/pow(2,10):.2f} KB'
    elif pow(2,20)<size<=pow(2,30):
        return f'{size/pow(2,20):.2f} MB'
    elif pow(2,30)<size<=pow(2,40):
        return f'{size/pow(2,30):.2f} GB'
    else:
        return f'{size} B'

def chdir2desktop():
    """切换保存文件目录到桌面
    """
    if os.name == 'nt':
        desktop = os.path.join(os.environ['HOMEPATH'], 'Desktop')
    else:
        desktop = os.path.join(os.environ['HOME'], 'Desktop')
    os.chdir(desktop)
    print(os.getcwd())

class ProgressbarWindow(object):
    """创建进度条
    """
    def __init__(self, top):
        self.__top = top
        self.__top.title('正在接收文件...')
        self.draw()
    def draw(self):
        self.lbl_1 = Label(self.__top, text='正在接收文件...')
        self.lbl_1.pack()
        self.pb = ttk.Progressbar(self.__top, length=200, value=0)
        self.pb.pack(padx=10, pady=15)
        self.lbl_2 = Label(self.__top, text='0%')
        self.lbl_2.pack()
    def update(self, buf: int, size: int):
        self.pb['value'] += buf/size*100
        value = self.pb['value']
        self.lbl_2['text'] = f'{value/100:.2%}'
        self.__top.update()
