#!/usr/bin/python3


from atexit import register as atexit_register
from socket import socket as system_socket
from os import system

HOST = '127.0.0.1'
PORT = 1337



def initialize_worker_socket():
    """Returns a configured socket"""
    socket = system_socket()
    socket.connect((HOST, PORT))
    return socket


def task():
    """Placeholder for task until proper task is define by digest_task()"""
    pass

def digest_task():
    """Takes the task string as argument. Makes task() function available"""



def main():
    print("Starting worker")
    socket = initialize_worker_socket()
    atexit_register((lambda socket: socket.close()), socket)

    while True:
        response = socket.recv(1024) # this is blocking operation. socket is set to blocking.
        socket.sendall(response)
        print("echoed a message")




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
