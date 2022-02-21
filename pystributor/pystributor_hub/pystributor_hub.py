#!/usr/bin/python3

#from pystributor_args import args
from cryptography.fernet import Fernet
#from pystributor_task import task
#from inspect import getsource
from threading import Thread
from time import sleep
import socket

ENCRYPTION_KEY = "xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="

f = Fernet(ENCRYPTION_KEY)



'''def get_task():
    """Returns task a string so it can be sent to workers"""
    return getsource(task)

def get_args():
    """returns list of tuples to be distirbuted to workers"""
    return args


def get_pool():
    """returns workers in some form. wololoo."""'''





def listener():

    HOST = "0.0.0.0"
    #HOST = "192.168.1.46"#Laptop
    #HOST = "192.168.1.70"#Desktop pc
    PORT = 6337

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # automagically also closes socket
        sock.bind((HOST, PORT))
        sock.listen()
        connection, address = sock.accept() # this is blocking. now waiting for socket connection
        with connection:
            print("[Worker][Listener]: Connected by", address)
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                print("[Hub][Listener]: Received following data:", data)
                print("[Hub][Listener]: Trying to decrypt...")
                decrypted_data = f.decrypt(data)
                print("[Hub][Listener]: Decrypted data:", decrypted_data)
                connection.sendall(f.encrypt(decrypted_data))
                print("[Hub][Listener]: Sent the decryped message back to the hub t. worker")




def super_calculator():
    while True:
        print("[Hub][Super Calculator]: doing nothing...")
        sleep(10)




def main():
    print("[Hub][Main Process]: Hub starting")

    t1 = Thread(target=super_calculator)
    t2 = Thread(target=listener)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    print("[Hub][Main Process]: Started daemons")


    while True:
        sleep(10)

    #t1.join()
    #t2.join()








if __name__ == "__main__":
    main()
