import os
import socket
import threading
from copy import deepcopy

HOST = ''
PORT = 8000
BUFFER = 1024
ADDR = (HOST, PORT)

ADDRS = []
ADDR_CONN = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(ADDR)
s.listen(10)

def msg_handle(data, addr, conn):
    data = data.decode('utf-8')
    print(data)
    head,data,usrs = data.split('::')
    if head == 'ONLINE':
        addr_copy = deepcopy(ADDRS)
        addr_copy.remove(addr)
        conn.send('ONLINE::{}'.format(addr_copy).encode())
        del addr_copy
    elif head == 'MSG':
        print(usrs, type(usrs))
        for usr in eval(usrs):
            ADDR_CONN[usr].send(f'MSG::{data}'.encode())
        # conn.send('MSG:[{0}] {1}'.format(ctime(), data).encode())
    elif head == 'FILE':
        info = eval(data)
        name = info['name']
        size = info['size']
        for usr in eval(usrs):
            ADDR_CONN[usr].send(
                f'FILE::是否接收来自{addr}的文件\n{name} {size}\n是[Y]/否[N]'.encode()
            )
    elif head == 'IMG':
        pass

def link_solve(conn, addr):
    while 1:
        try:
            # data = conn.recv(BUFFER).decode('utf-8')
            data = conn.recv(BUFFER)
            if not data:
                break
            msg_handle(data, addr, conn)
        except ConnectionResetError as e:
            print(f'{e}')
            print(f'{addr} offline.')
            ADDRS.remove(addr)
            ADDR_CONN.pop(addr)
            break
    conn.close()

def recv_data():
    while 1:
        print('waiting for connection...')
        conn, addr = s.accept()
        print('...connecting from:', addr)
        if addr not in ADDRS:
            ADDRS.append(addr)
            ADDR_CONN[addr] = conn
        t = threading.Thread(target=link_solve,args=(conn, addr))
        t.start()
    s.close()


if __name__ == '__main__':
    t1 = threading.Thread(target=recv_data, args=())
    t1.start()
