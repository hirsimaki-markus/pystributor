#!/usr/bin/python3


from atexit import register as atexit_register
from hmac import digest
from socket import socket as system_socket, SHUT_RDWR
from os import system
from json import loads, dumps

HOST = '127.0.0.1'
PORT = 1337
BUFF_SIZE = 4096 # 4kB






# !!!! THIS true_exec BLOCK IS COPIED FROM SEAPIE !!!!!
# https://github.com/hirsimaki-markus/SEAPIE
# the author of seapie is Markus Hirsimäki, same author as in the course group
def true_exec(code, scope):
    """exec() a codeblock in given scope. Used by seapi repl
    scope 0 equals executing in context of caller of true_exec().
    scope 1 equals executing in context of the caller for the caller
    of true_exec().
    """


    import sys
    import traceback
    from ctypes import pythonapi, py_object, c_int


    parent = sys._getframe(scope+1)  # +1 escapes true_exec itself
    parent_globals = parent.f_globals
    parent_locals = parent.f_locals
    try:
        exec(code, parent_globals, parent_locals)
    except KeyboardInterrupt:  # emulate ctrl+c if code='input()'
        print("\nKeyboardInterrupt")
    except Exception:  # catch arbitary exceptions from exec
        traceback.print_exc()
    # beware traveller. here lies dark spell of the olden times !
    # the following call forces update to locals()
    # adding new variables is allowed but calling them requires
    # some indirection like using exec() or a placeholder
    # otherwise you will get nameError when calling the variable
    # the magic value 1 stands for ability to introduce new
    # variables. 0 for update-only
    pythonapi.PyFrame_LocalsToFast(py_object(parent), c_int(1))
















def initialize_worker_socket():
    """Returns a configured socket"""
    socket = system_socket()
    socket.connect((HOST, PORT))
    return socket


def task(arg):
    """Placeholder for task until proper task is define by digest_task()"""
    # not working yet!
    return "wololooo!"


def digest_task(task_str):
    """Takes the task string as argument. Makes task() function available"""
    #print("tryina digest")
    #print(task_str)
    true_exec(task_str, 2)


def recvall_worker(socket):
    """Receive all data from socket. Detects EOF. Worker and hub in lockstep."""
    accum = b''


    # the packets sent must be json so they end in } otherwise error checking wont work
    # TODO: prefix messages with their lenght. make recv buffer bigger.

    while True:
        #print("APUUAAAAAAAA!!!!!"*100)
        try:
            part = socket.recv(4096)
        except BlockingIOError:
            # blockin happens if nothing to read and last message len == buffer
            # so it keeps waiting for next packet even tho nothing is coming
            if accum[-1] == ord("}"): # timeout since last len() for last part equls buff size. waiting for next acket forever
                break
            else:
                print("\n\nWarning!!! Reading worker response failed. Received only part of package before timeout")
                print("Package might have been (partially) lost during transit or connection is bad")
                continue
                # this continue should never happen. selector told connection is ready to read
                # we can reasonably expect that the whole "packet" has already been received
                # in timely manner before timeout should happen. this means that connection somehow failed
                # or the data being sent over the stream is extremely large or is being split into small
                # chunks and being slowed down too much by some network device
        #print(part, end=" ")
        accum += part
        #print(len(part), BUFF_SIZE)
        if len(part) < BUFF_SIZE:
            break # part was 0 or part was last

    return accum


def exit_handler(socket):
    try:
        socket.shutdown(SHUT_RDWR)
    except OSError as e:
        if e.errno == 107:
            pass # socket already closed


def main():
    print("Starting worker")
    socket = initialize_worker_socket()
    atexit_register(exit_handler, socket)

    while True:
        packet = recvall_worker(socket)

        if packet == b'':
            print("Received end of file. Shutting down.")
            break

        # client and server in lockstep > can pick single "message" from stream
        message = loads(packet.decode("utf-8"))
        if "task" in message: # sending back back ok since task was received
            digest_task(message["task"])
            message = {"task": "ok"}
            packet = dumps(message).encode("utf-8")
            socket.sendall(packet)
            print("Received and digested task. Ack sent.")
        elif "arg" in message: # sending back and answer to an argument
            #print("received arg")
            argument = message["arg"]
            #print(argument)
            task_result = task(argument)
            message = {"arg": argument, "ans": task_result}
            packet = dumps(message).encode("utf-8")
            socket.sendall(packet)
            #print("Processed argument:", argument, task_result, "Ack sent.")
            #print("managed to send stuff yo")



if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix

    from time import time
    alku = time()

    main()

    print("kesto:", time()-alku)







#############[ trash code ]###############
#
#
#from cryptography.fernet import Fernet
#from threading import Thread
#from time import sleep
#import socket
#
#ENCRYPTION_KEY = "xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="
#HOST = "127.0.0.1"
#PORT = 1338
##HOST = "192.168.1.46"#Laptop
##HOST = "192.168.1.70"#Desktop pc
#
#def main():
#    print("[Worker][Main Process]: Worker starting")
#
#    fernet = Fernet(ENCRYPTION_KEY)
