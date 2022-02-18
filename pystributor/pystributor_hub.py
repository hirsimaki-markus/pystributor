#!/usr/bin/python3

from pystributor_args import args
from cryptography.fernet import Fernet
from pystributor_task import task
from inspect import getsource
from threading import Thread
from time import sleep
import socket



import selectors
import types




ENCRYPTION_KEY = "xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="
#HOST = "0.0.0.0" # listen to all incoming traffic
HOST = "127.0.0.1"
PORT = 1337
#HOST = "192.168.1.46"#Laptop
#HOST = "192.168.1.70"#Desktop pc


sel = selectors.DefaultSelector()


def get_task():
    """Returns task a string so it can be sent to workers"""
    return getsource(task)

def get_args():
    """returns list of tuples to be distirbuted to workers"""
    return args


def get_pool():
    """returns workers in some form. wololoo."""
    pass






def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    #print("did some servicing yo")
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]










def super_calculator():
    input("hold it bruda")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            message = input("send something from worker: ")
            message = message.encode('utf-8')
            s.sendall(message)
            #data = s.recv(1024)
            #print(data)

    #while True:
    #    print("supercalc idling")
    #    sleep(10)


    #with connection:
    #    while True:
    #        data = connection.recv(4096)
    #        if not data:
    #            break
    #        print("[Worker][Listener]: Received following data:", data)
    #        print("[Worker][Listener]: Trying to decrypt...")
    #        decrypted_data = fernet.decrypt(data)
    #        print("[Worker][Listener]: Decrypted data:", decrypted_data)
    #        connection.sendall(fernet.encrypt(decrypted_data))
    #        print("[Worker][Listener]: Sent the decryped message back to the hub t. worker")












def listener():
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()




def main():
    print("[Hub][Main Process]: Hub starting")

    fernet = Fernet(ENCRYPTION_KEY)





    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    #print('listening on', (host, port))
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, data=None)




    print("[Hub][Main Process]: Starting daemons")

    t1 = Thread(target=super_calculator)
    t2 = Thread(target=listener)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()




    #print()
    #print()
    #print(get_task())
    #print()
    #print(get_args())
    #print()
    #print()


    while True:
        print("main thead idling")
        sleep(10)

    #t1.join()
    #t2.join()








if __name__ == "__main__":
    main()
