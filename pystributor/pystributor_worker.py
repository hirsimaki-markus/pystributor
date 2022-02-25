#!/usr/bin/python3


from atexit import register as atexit_register
from hmac import digest
from socket import socket as system_socket
from os import system
from json import loads, dumps

HOST = '127.0.0.1'
PORT = 1337







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
    buffer_bytes = 8
    accum = b''
    while True:
        part = socket.recv(8)
        accum += part
        if len(part) < buffer_bytes:
            break # part was 0 or part was last
    return accum




def main():
    print("Starting worker")
    socket = initialize_worker_socket()
    atexit_register((lambda socket: socket.close()), socket)

    while True:
        packet = recvall_worker(socket)
        # client and server in lockstep > can pick single "message" from stream
        message = loads(packet.decode("utf-8"))
        if "task" in message:
            print("received task")
            digest_task(message["task"])
            message = {"task": "ok"}
            packet = dumps(message).encode("utf-8")
            socket.sendall(packet)
        elif "arg" in message:
            print("received arg")
            task_result = task(message["arg"])
            message = {"arg": task_result}
            packet = dumps(message).encode("utf-8")
            socket.sendall(packet)



if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    main()







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
