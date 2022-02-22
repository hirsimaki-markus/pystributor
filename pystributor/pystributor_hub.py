#!/usr/bin/python3

from selectors import DefaultSelector, EVENT_READ
from atexit import register as atexit_register
from socket import socket as system_socket
from threading import Thread
from inspect import getsource
from time import sleep
from os import system



HOST = "0.0.0.0" # listen to all incoming traffic. 127.0.0.1 if localhost only
PORT = 1337


def get_task():
    """Returns task as a string so it can be distributed to workers"""
    from pystributor_task import task
    return getsource(task)

def get_args():
    """returns list of tuples to be distirbuted to workers as arguments"""
    from pystributor_args import args
    return args




def initialize_socket():
    """Returns a configured socket"""
    socket = system_socket()
    socket.setblocking(False) # blocking would prevent ctrl+c on windows
    socket.bind((HOST, PORT))
    return socket


def discover_workers(socket):
    """Waits for workers to connect. Returns worker pool when interrupted"""
    pool = []
    print("Building worker pool. Waiting for workers to come online.", end="")
    print(" Start workers now.\n")
    print("!!! Press <ctrl+c> to stop waiting for more workers to join !!!\n")
    socket.listen(0) # backlog = 0
    try:
        while True:
            try:
                connection, address = socket.accept()
            except BlockingIOError:
                # socket is set to nonblocking. error happens in loop
                # this allows for ctrl+c to work also on windows
                continue
            connection.setblocking(False) # must be nonblocking for selector
            pool.append((connection, address))
            print("Added worker to pool. Worker address is", address[0] + ":"
                  + str(address[1]) + ".", "Pool size is now", len(pool), )
    except KeyboardInterrupt:
        print("\n\nDone building worker pool. Pool size:", len(pool))
    return pool



def listener(pool):
    """Handles getting replies from workers"""
    print("Listener daemon online. Waiting for worker replies.")
    connection_selector = DefaultSelector()
    # selector can be queried for file descriptors waiting for I/O operations
    # one selector will handle up to 1024 workers
    for connection, address in pool:
        connection_selector.register(connection, EVENT_READ)
    def _selector_read_handler(connection, mask):
        """Handles data read by selector from connections"""
        data = connection.recv(1024)
        if data:
            # there must be data; select() returns connectons waiting for read
            print("received stuff. awesome.", data)
        else: # connection is likely closing since no data
            print("Closing worker connection")
            connection_selector.unregister(connection)
            connection.close()
    while True:
        for selectorkey, mask in connection_selector.select(): # this blocks. timeout can be argument. selectorkeys are stuff that has data waiting.
            connection = selectorkey.fileobj
            _selector_read_handler(connection, mask)



def super_calculator(pool):
    """The brain which distributes tasks to workers in pool"""
    print("Super calculator daemon online. Distributing tasks to workers.")
    while True:
        for connection, address in pool:
            msg = "Test message to " + address[0] + ":" + str(address[1])
            connection.sendall(msg.encode("utf-8"))
            print("sent:", msg)
        sleep(5)
        print()



def main():
    print("Starting hub")
    socket = initialize_socket()
    atexit_register((lambda socket: socket.close()), socket)
    pool = discover_workers(socket)
    print("Hub initialized. Starting daemons.")
    Thread(target=super_calculator, args=[pool], daemon=True).start()
    Thread(target=listener, args=[pool], daemon=True).start()
    while True: sleep(1)



if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
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



#############################[ trash code ]################################



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
