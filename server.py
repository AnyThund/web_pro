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

FILE_RECV = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(ADDR)
s.listen(10)

def msg_handle(data, conn: socket.socket, addr: tuple):
    try:
        data = data.decode('utf-8')
        try:
            head,data,usrs = data.split('::')
        except (TypeError, ValueError):
            print('Transmitting file...')
            data = data.encode()
            head = ''
    except UnicodeDecodeError:
        print('Transmitting file...')
        head = ''
    if head == 'ONLINE':
        addr_copy = deepcopy(ADDRS)
        addr_copy.remove(addr)
        conn.send('ONLINE::{}'.format(addr_copy).encode())
        del addr_copy
    elif head == 'MSG':
        print(usrs, type(usrs))
        for usr in eval(usrs):
            try:
                ADDR_CONN[usr].send(f'MSG::{data}'.encode())
            except OSError:
                ADDR_CONN.pop(usr)
        # conn.send('MSG:[{0}] {1}'.format(ctime(), data).encode())
    elif head == 'FILE':
        FILE_RECV.clear()
        if data == 'OK':
            usr = eval(usrs)
            FILE_RECV.append(addr)
            ADDR_CONN[usr].send(f'FILE::OK'.encode())
        else:
            for usr in eval(usrs):
                ADDR_CONN[usr].send(f'FILE::{data};;{addr}'.encode())
        # t = threading.Thread(target=file_handle, args=(data,usrs,conn,addr))
        # t.start()
    elif head == 'IMG':
        FILE_RECV.clear()
        for usr in eval(usrs):
            FILE_RECV.append(usr)
            ADDR_CONN[usr].send(f'IMG::{data};;{addr}'.encode())
        print(usrs)
    else:
        # print(data, type(data))
        for usr in FILE_RECV:
            ADDR_CONN[usr].send(data)

def link_solve(conn: socket.socket, addr: tuple):
    while 1:
        try:
            # data = conn.recv(BUFFER).decode('utf-8')
            data = conn.recv(BUFFER)
            if not data:
                break
            msg_handle(data, conn, addr)
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
