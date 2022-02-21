#!/usr/bin/python3


from socket import socket as get_socket
from os import system
from sqlite3 import connect
from threading import Thread
from time import sleep
import atexit


#########selector test####
import selectors
MY_SELECTOR = selectors.DefaultSelector()
def SELECTOR_READ(connection, mask):
    #client_address = connection.getpeername()
    #print('read({})'.format(client_address))
    data = connection.recv(1024)
    if data:
        # A readable client socket has data
        print("received stuff. awesome.", data)
        #print('  received {!r}'.format(data))
    else:
        # Interpret empty result as closed connection
        print('  closing')
        MY_SELECTOR.unregister(connection)
        connection.close()
        # Tell the main loop to stop
        #keep_running = False
################






HOST = "127.0.0.1"
PORT = 1337
#HOST = "0.0.0.0" # listen to all incoming traffic




def discover_workers(socket):
    """Begin listening for workers. Adds connections to pool until manually stopped. Returns pool"""
    print("Building worker pool. Waiting for workers to come online.\n")
    print("Press <ctrl+c> to end discovery and move forward.\n")

    pool = []

    socket.listen(0) # backlog = 0
    try:
        while True:
            try:
                connection, address = socket.accept()
            except BlockingIOError: # socket set to nonblocking. busy wait with try except, otherwise socket.accept block even ctrl+c (on windows)
                continue


            # selector test begin
            connection.setblocking(False)
            MY_SELECTOR.register(connection, selectors.EVENT_READ, SELECTOR_READ) # last argument can be anything to be associated with the file object. here its callback.

            # selector test end


            pool.append((connection, address))
            print("Added worker to pool. Worker address is", address[0] + ":" + str(address[1]) + ".", "Pool size is now", len(pool), )
    except KeyboardInterrupt:
        print("\n\nDone building worker pool. Pool size:", len(pool))




    return pool





def listener():
    print("listener online!")
    while True:
        for selectorkey, mask in MY_SELECTOR.select(): # this blocks. timeout can be argument.
            callback = selectorkey.data # data stores arbitrary stuff assosiated with the the filedescriptor
            connection = selectorkey.fileobj
            callback(connection, mask)





def super_calculator(pool):
    while True:
        for connection, address in pool:
            msg = "Test message to " + address[0] + ":" + str(address[1])
            connection.sendall(msg.encode("utf-8"))
            print("sent:", msg)
        sleep(5)
        print()



def main():
    _ = system("cls||clear") # clear screen on windows and unix

    socket = get_socket()
    socket.setblocking(False)
    socket.bind((HOST, PORT))


    pool = discover_workers(socket)

    atexit.register((lambda: socket.close()), socket)

    t_suprcalc = Thread(target=super_calculator, args=[pool])
    t_listener = Thread(target=listener, args=[])
    t_suprcalc.daemon = True
    t_listener.daemon = True
    print("\nStarting daemons. Main thread idle.\n")
    t_listener.start()
    t_suprcalc.start()

    while True:
        sleep(10)


    print("main thread end?")

if __name__ == "__main__":
    main()













################[ not trash code]################################

# fernet = Fernet(ENCRYPTION_KEY)
# ENCRYPTION_KEY = "xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="

#from pystributor_args import args
#from cryptography.fernet import Fernet
#from pystributor_task import task
#from inspect import getsource
#from threading import Thread
#from time import sleep
#import socket

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.bind((HOST, PORT))
#sock.listen()
#print('listening on', (host, port))
#sock.setblocking(False)
#sel.register(sock, selectors.EVENT_READ, data=None)

#t1.join()
#t2.join()

#############################[ trash code ]################################
#def get_task():
#    """Returns task a string so it can be sent to workers"""
#    return getsource(task)

#def get_args():
#    """returns list of tuples to be distirbuted to workers"""
#    return args


#def get_pool():
#    """returns workers in some form. wololoo."""
#    pass


# def accept_wrapper(sock):
#     conn, addr = sock.accept()  # Should be ready to read
#     print('accepted connection from', addr)
#     conn.setblocking(False)
#     data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
#     events = selectors.EVENT_READ | selectors.EVENT_WRITE
#     sel.register(conn, events, data=data)
#
# def service_connection(key, mask):
#     #print("did some servicing yo")
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)  # Should be ready to read
#         if recv_data:
#             data.outb += recv_data
#         else:
#             print('closing connection to', data.addr)
#             sel.unregister(sock)
#             sock.close()
#     if mask & selectors.EVENT_WRITE:
#         if data.outb:
#             print('echoing', repr(data.outb), 'to', data.addr)
#             sent = sock.send(data.outb)  # Should be ready to write
#             data.outb = data.outb[sent:]
#
# def super_calculator():
#     #input("hold it bruda")
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect(("127.0.0.1", 1338))
#         while True:
#             message = input("send something from worker: ")
#             message = message.encode('utf-8')
#             s.sendall(message)
#             #data = s.recv(1024)
#             #print(data)
#
#     #while True:
#     #    print("supercalc idling")
#     #    sleep(10)
#
#
#     #with connection:
#     #    while True:
#     #        data = connection.recv(4096)
#     #        if not data:
#     #            break
#     #        print("[Worker][Listener]: Received following data:", data)
#     #        print("[Worker][Listener]: Trying to decrypt...")
#     #        decrypted_data = fernet.decrypt(data)
#     #        print("[Worker][Listener]: Decrypted data:", decrypted_data)
#     #        connection.sendall(fernet.encrypt(decrypted_data))
#     #        print("[Worker][Listener]: Sent the decryped message back to the hub t. worker")
