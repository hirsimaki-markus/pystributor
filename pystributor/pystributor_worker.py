#!/usr/bin/python3




import socket
from os import system

HOST = '127.0.0.1'
PORT = 1337

def clear_screen():
    """Clear screen on unix and windows platforms"""
    _ = system("cls||clear")

clear_screen()
print("Worker started. Waiting for messages.")

ClientSocket = socket.socket()


ClientSocket.connect((HOST, PORT))

while True:
    response = ClientSocket.recv(1024) # this is blocking operation. socket is set to blocking.
    ClientSocket.sendall(response)
    print("Got message from hub and sent it back:", response.decode('utf-8'))






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
#
#
#
#def calculator():
#    while True:
#        print("listenre doing nothing")
#        sleep(10)
#
#
#
#
#def listener():
#    #while True:
#    #    print("listenre doing nothing")
#    #    sleep(10)
#
#    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#    #    sock.connect((HOST, PORT))
#    #    while True:
#            #message = input("[Hub][S Calculator]: Something to send from hub to worker: ")
#            #message = message.encode('utf-8')
#            #encypted_message = f.encrypt(message)
#
#            #data = sock.recv(4096)
#            #sock.sendall(data)
#
#            #print("[Hub][S Calculator]: Received stuff back from worker", repr(data))
#            #print("[Hub][S Calculator]: Decrypted version: ", f.decrypt(data))
#
#
#    echoSocket = socket.socket()
#    echoSocket.bind(("127.0.0.1", 1338))
#    echoSocket.listen()
#    while(True):
#        (clientSocket, clientAddress) = echoSocket.accept()
#        while(True):
#            data = clientSocket.recv(1024)
#            print("At Server: %s"%data)
#            if(data!=b''):
#                # Send back what you received
#                clientSocket.send(data)
#                break
#
#
#def main():
#    print("[Worker][Main Process]: Worker starting")
#
#    fernet = Fernet(ENCRYPTION_KEY)
#
#
#
#    print("[Worker][Main Process]: Starting daemons")
#
#
#    t1 = Thread(target=calculator)
#    t2 = Thread(target=listener)
#    t1.daemon = True
#    t2.daemon = True
#    t1.start()
#    t2.start()
#
#
#
#
#    while True:
#        sleep(10)
#
#    #t1.join()
#    #t2.join()
#
#
#if __name__ == "__main__":
#    main()
