#!/usr/bin/python3


from cryptography.fernet import Fernet
from threading import Thread
from time import sleep
import socket

ENCRYPTION_KEY = "xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="
f = Fernet(ENCRYPTION_KEY)

def calculator():
    while True:
        print("[Worker][Calculator]: doing nothing...")
        sleep(10)



def listener():

    HOST = "127.0.0.1"
    #HOST = "192.168.1.46"#Laptop
    #HOST = "192.168.1.70"#Desktop pc
    PORT = 1337

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
                print("[Worker][Listener]: Received following data:", data)
                print("[Worker][Listener]: Trying to decrypt...")
                decrypted_data = f.decrypt(data)
                print("[Worker][Listener]: Decrypted data:", decrypted_data)
                connection.sendall(f.encrypt(decrypted_data))
                print("[Worker][Listener]: Sent the decryped message back to the hub t. worker")






def main():
    print("[Hub][Main Process]: Hub starting")

    t1 = Thread(target=calculator)
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
