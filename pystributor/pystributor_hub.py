#!/usr/bin/python3


from cryptography.fernet import Fernet
from threading import Thread
from time import sleep
import socket

from pystributor_task import task

ENCRYPTION_KEY = "xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="
f = Fernet(ENCRYPTION_KEY)






def super_calculator():


    HOST = "127.0.0.1"
    PORT = 1337

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        while True:
            message = input("[Hub][S Calculator]: Something to send from hub to worker: ")
            message = message.encode('utf-8')
            encypted_message = f.encrypt(message)
            sock.sendall(encypted_message)
            data = sock.recv(1024)
            print("[Hub][S Calculator]: Received stuff back from worker", repr(data))
            print("[Hub][S Calculator]: Decrypted version: ", f.decrypt(data))







def listener():
    while True:
        print("[Hub][Con Listener]: doing nothing...")
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






# supercalculator
# listener