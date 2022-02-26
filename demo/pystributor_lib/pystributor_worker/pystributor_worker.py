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
    #HOST = "127.0.0.1"
    #HOST = "192.168.1.46"#Laptop
    HOST = "192.168.1.70"#Desktop pc
    PORT = 6337

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        while True:
            message = input("[Hub][S Calculator]: Something to send from worker to hub: ")
            message = message.encode('utf-8')
            encypted_message = f.encrypt(message)
            sock.sendall(encypted_message)
            data = sock.recv(1024)
            print("[Worker][Listener]: Received stuff back from worker", repr(data))
            print("[Worker][Listener]: Decrypted version: ", f.decrypt(data))






def main():
    print("[Worker][Main Process]: Worker starting")

    t1 = Thread(target=calculator)
    t2 = Thread(target=listener)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    print("[Worker][Main Process]: Started daemons")


    while True:
        sleep(10)

    #t1.join()
    #t2.join()





if __name__ == "__main__":
    main()
