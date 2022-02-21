#!/usr/bin/python3

import socket
import os
from _thread import *

maken_yhteydet = []

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection):
    connection.send(str.encode('Welcome to the Servern'))
    while True:

        data = connection.recv(2048)
        print(data)
        reply = 'Server Says: ' + data.decode('utf-8')
        if not data:
            break
        connection.sendall(str.encode(reply))

        #if data == b'':
        #    connection.close()
        #    break
    connection.close()

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    maken_yhteydet.append(Client)
    print('Thread Number: ' + str(ThreadCount))


    if ThreadCount == 2:
        break


while True:
    something_to_send = input("give something pls: ")
    connection1 = maken_yhteydet[0]
    connection2 = maken_yhteydet[1]
    connection1.sendall(str.encode(something_to_send))
    connection2.sendall(str.encode(something_to_send))

ServerSocket.close()

