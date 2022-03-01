#!/usr/bin/python3


from atexit import register as atexit_register
from socket import socket as system_socket, SHUT_RDWR
from os import system
from json import loads, dumps
from time import sleep
from cryptography.fernet import Fernet

class Hub:
    def __init__(self, host="127.0.0.1", port=1337, buff_size=4096, fernetkey="xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="):
        self.host = host
        self.port = port
        self.buff_size = buff_size
        self.fernetkey = fernetkey

        self.socket = None # initialized on socket startup
        self.fernet = None # initialized on socket startup
        self.task = None # initialized when hub provides a task

    def initialize_worker_socket(self):
        """Returns a configured socket"""
        socket = system_socket()
        #socket.connect((HOST, PORT))
        while True:
            try:
                socket.connect((self.host, self.port))
            except Exception as e:
                print("Cannot connect to hub yet, trying again in 1 second.")
                #print(e)
                sleep(1)
                input("venaan ikuisesti :DDDDD")
            else:
                print("Connected to hub")
                break
        self.socket = socket

    def initialize_fernet(self):
        self.fernet = Fernet(self.fernetkey)

    def recvall_worker(self):
        """Receive all data from socket. Detects EOF. Worker and hub in lockstep."""
        accum = b''
        # the packets sent must be json so they end in } otherwise error checking wont work
        # TODO: prefix messages with their lenght. make recv buffer bigger.
        while True:
            try:
                part = self.socket.recv(self.buff_size)
            except BlockingIOError:
                # blockin happens if nothing to read and last message len == buffer
                # so it keeps waiting for next packet even tho nothing is coming
                break
                # this continue should never happen. selector told connection is ready to read
                # we can reasonably expect that the whole "packet" has already been received
                # in timely manner before timeout should happen. this means that connection somehow failed
                # or the data being sent over the stream is extremely large or is being split into small
                # chunks and being slowed down too much by some network device
            accum += part
            if len(part) < self.buff_size:
                break # part was 0 or part was last
        return accum

    def exit_handler(self):
        try:
            self.socket.shutdown(SHUT_RDWR)
        except OSError as e:
            if e.errno == 107:
                pass # socket already closed

    def start(self):
        print("Starting worker. Trying to connect to the hub on adress:", self.host, ", port",  self.port)
        self.initialize_fernet()
        self.initialize_worker_socket()
        atexit_register(self.exit_handler)
        while True:
            packet_encrypted = self.recvall_worker()
            if packet_encrypted == b'':
                print("Received end of file. Shutting down.")
                break
            packet = self.fernet.decrypt(packet_encrypted)
            # client and server in lockstep > can pick single "message" from stream
            message = loads(packet.decode("utf-8"))
            if "task" in message: # sending back back ok since task was received
                self.task = message["task"]
                message = {"task": "ok"}
                encrypted_packet = self.fernet.encrypt(dumps(message).encode("utf-8"))
                self.socket.sendall(encrypted_packet)
                print("Received and digested task. Ack sent.")
            elif "arg" in message: # sending back and answer to an argument
                argument = message["arg"]
                # wicked smaht vvvvvvv
                exec(self.task + f"\n\nx = task({argument})")
                task_result = locals()['x']
                # wicked smath ^^^^^^
                message = {"arg": argument, "ans": task_result}
                encrypted_packet = self.fernet.encrypt(dumps(message).encode("utf-8"))
                self.socket.sendall(encrypted_packet)
