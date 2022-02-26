#!/usr/bin/python3


"""Important: worker pool data type is currently implemented as 2D list
[[connection, address, is_ready], [...], [...]]
The data should be accessed with list notation by enumerating worker pool if
needed. both lists are mutable so the nonglobal pool can be passed by reference
"""


from selectors import DefaultSelector, EVENT_READ
from atexit import register as atexit_register
from socket import socket as system_socket, SHUT_RDWR
from threading import Thread
from inspect import getsource
from time import sleep
from os import system
from json import loads, dumps
from cryptography.fernet import Fernet



HOST = "0.0.0.0" # listen to all incoming traffic. 127.0.0.1 if localhost only
PORT = 1337
BUFF_SIZE = 4096 # 4kB
FERNETKEY = "xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="
ANSWERSHEET = {}


def get_task():
    """Returns task as a string so it can be distributed to workers"""
    from pystributor_task import task
    return getsource(task)

def get_args():
    """returns list of tuples to be distirbuted to workers as arguments"""
    from pystributor_args import args
    return args


def recvall_hub(connection):
    """Receive all data from connection. Detects EOF. Worker and hub in lockstep."""

    accum = b''

    # the packets sent must be json so they end in } otherwise error checking wont work
    # TODO: prefix messages with their lenght. make receive buffer bigger
    # or maybe lazy solution is to try and validate the json object that has been fetched. ez

    while True:
        try:
            part = connection.recv(BUFF_SIZE)
        except BlockingIOError:
            # blockin happens if nothing to read and last message len == buffer
            # so it keeps waiting for next packet even tho nothing is coming
            # timeout since last len() for last part equls buff size. waiting for next acket forever
            break
            # this continue should never happen. selector told connection is ready to read
            # we can reasonably expect that the whole "packet" has already been received
            # in timely manner before timeout should happen. this means that connection somehow failed
            # or the data being sent over the stream is extremely large or is being split into small
            # chunks and being slowed down too much by some network device
        accum += part
        #print(len(part), buffer_bytes)
        if len(part) < BUFF_SIZE:
            break # received part was smaller than buffer size > message must be over

    #socket.setblocking(False)
    #connection.setblocking(False)

    return accum



    #    try:
    #        part = connection.recv(8)
    #    except BlockingIOError as e:
    #        err = e.args[0]
    #        if err == EAGAIN or err == EWOULDBLOCK:
    #            continue
    #        else:
    #            # a "real" error occurred
    #            print(e)
    #            exit()




def initialize_server_socket():
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
            pool.append([connection, address, None]) # worker status is undefine. it has not responded yet
            print("Added worker to pool. Worker address is", address[0] + ":"
                  + str(address[1]) + ".", "Pool size is now", len(pool), )
    except KeyboardInterrupt:
        print("\n\nDone building worker pool. Pool size:", len(pool))
    return pool


def distribute_task(pool, fernet):
    """Distribute task to workers"""
    for connection, _address, _ready in pool:
        #connection, _address, _ready = worker
        task_str = get_task()
        message = {"task": task_str}
        packet = fernet.encrypt(dumps(message).encode("utf-8"))
        # client and server in lockstep > can send single "message" to stream
        connection.sendall(packet)
        #pool[i][2] = True # set worker readiness to True



def listener(pool, fernet):
    """Handles getting replies from workers"""
    print("Listener daemon online. Waiting for worker replies.")
    connection_selector = DefaultSelector()
    # selector can be queried for file descriptors waiting for I/O operations
    # one selector will handle up to 1024 workers
    for i, worker in enumerate (pool):
        connection, _address, _ready = worker
        connection_selector.register(connection, EVENT_READ, i)
    def _selector_read_handler(connection, pool, worker_idx):
        """Handles data read by selector from connections"""
        encrypted_packet = recvall_hub(connection)
        if encrypted_packet: # if not empty
            packet = fernet.decrypt(encrypted_packet)



            # there must be data; select() returns connectons waiting for read
            #print()
            #print("received stuff. awesome.", connection.getpeername())
            #print()

            # client and server in lockstep > can pick single "message" from stream
            message = loads(packet.decode("utf-8"))
            if "task" in message:
                # task was received succesfully
                if message["task"] == "ok":
                    pool[worker_idx][2] = True
            elif "arg" in message:
                # received answer to a calculation
                question = message["arg"]
                answer = message["ans"]
                pool[worker_idx][2] = True
                ANSWERSHEET[question] = answer
                #print(len(ANSWERSHEET))
                #print(len(get_args()))


        else: # connection is likely closing since no data
            print("Closing worker connection. Worker dropped from pool.")
            connection_selector.unregister(connection)
            connection.close()
            #pool[worker_idx][2] = False
            #print("Worker state marked as False")
            #print(pool[worker_idx])
            #TODO:hub and worker still breaks if worker is dropped at any point...

    arg_count = len(get_args())
    while True:
        for selectorkey, mask in connection_selector.select(): # this blocks. timeout can be argument. selectorkeys are stuff that has data waiting.
            connection = selectorkey.fileobj
            worker_idx = selectorkey.data
            _selector_read_handler(connection, pool, worker_idx)
        if arg_count == len(ANSWERSHEET):
            break
    print("Listener daemon done. All answers received.")




def super_calculator(pool, fernet):
    """The brain which distributes tasks to workers in pool"""
    print("Super calculator daemon online. Distributing tasks to workers.")
    distribute_task(pool, fernet)
    class NestedLoopException(Exception):
        """raised to close nested loop"""
        pass
    arguments_for_workers = get_args()
    for argument in arguments_for_workers: # for all arguments
        try:
            while True: # until argument is sent
                for i, worker in enumerate(pool): # until worker is found
                    connection, _address, ready = worker
                    if not ready:
                        continue


                    message = {"arg": argument[0]} # TODO: vararg support for n arguments
                    packet = fernet.encrypt(dumps(message).encode("utf-8"))
                    connection.sendall(packet)

                    pool[i][2] = False # worker readiness is false

                    # print("sent packet to worker", i)
                    raise NestedLoopException
        except NestedLoopException:
            #print("perkele"*10)
            continue

    print("Calculator daemon done. All arguments distributed.")


def kill_workers(pool):
    """Send message to each worker to exit"""
    for i, worker in enumerate(pool):
        connection, _address, _ready = worker
        connection.close()
        pool[i][2] = False # worker readiness is false


def exit_handler(socket):
    try:
        socket.shutdown(SHUT_RDWR)
    except OSError as e:
        if e.errno == 107:
            pass # socket already closed


def main():
    print("Starting hub")
    fernet = Fernet(FERNETKEY)
    socket = initialize_server_socket()
    atexit_register(exit_handler, socket)
    pool = discover_workers(socket)


    ### timing test ###
    from time import time
    alku = time()
    _=input("Enter to start timing")
    ###################

    print("Hub initialized. Starting listener and calculator daemons. Waiting for daemons to finish.")
    (t1 := Thread(target=super_calculator, args=[pool, fernet], daemon=True)).start()
    (t2 := Thread(target=listener, args=[pool, fernet], daemon=True)).start()

    while (t1.is_alive() or t2.is_alive()):
        # wait until all arguments have bee sent to workers and wait until
        # all arguments have been processed
        sleep(1)

    print("Daemons done. Killing workers.")
    kill_workers(pool)

    print("==========[ Results for task per argument]==========")
    #for key in ANSWERSHEET:
    #    print(key, ":", ANSWERSHEET[key])


    ### timing test ###
    print("kesto:", time()-alku)
    ###################





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


















# TÖYT TÄHÄN ASTI: 18H PER NASSU
# ja makelle ehkä 3h lisää