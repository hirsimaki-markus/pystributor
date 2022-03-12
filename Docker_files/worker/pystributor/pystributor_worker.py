#!/usr/bin/python3

from socket import socket as system_socket, SHUT_RDWR
from atexit import register as atexit_register
from cryptography.fernet import Fernet
from json import loads, dumps
from time import sleep
from os import system

class Worker:
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
            except ConnectionRefusedError:
                print("Cannot connect to hub yet, trying again in 1 second.")
                sleep(1)
            else:
                print("Connected to hub")
                break
        self.socket = socket

    def initialize_fernet(self):
        self.fernet = Fernet(self.fernetkey)

    def recvall_worker(self):
        """Receive all data from connection. Detects EOF, not message delimeter.

        Worker and hub are in lockstep; currently no need for message start
        and end symbols. Safe to assume messages are received as intended.
        If features like heartbeat for workers are added this function needs
        updating
        """
        accum = b''
        # TODO: prefix messages with their lenght.
        while True:
            try:
                part = self.socket.recv(self.buff_size)
            except BlockingIOError:
                # blocking happens if nothing to read and last message
                # len == buffer so it keeps waiting for next packet even
                # though nothing is coming. timeout since last len() for last
                # part equls buff size. waiting for next acket forever
                break
                # esle continue should never happen. selector told connection
                # is ready to read we can reasonably expect that the whole
                # "packet" has already been received in timely manner before
                # timeout should happen. this means that connection somehow
                # failed or the data being sent over the stream is extremely
                # large or is being split into small chunks and being slowed
                # down too much by some network device
            accum += part
            if len(part) < self.buff_size:
                break
                # received part was smaller than buffer size
                # so message must be over. this assumption fails if changes
                # are made and hub-workers are not in lockstep anymore
        return accum

    def exit_handler(self):
        """Cleanly released socket back to os"""
        try:
            self.socket.shutdown(SHUT_RDWR)
        except OSError as e:
            if e.errno == 107:
                pass # socket already closed

    def send_json_message(self, json_str):
        encrypted_packet = self.fernet.encrypt(dumps(json_str).encode("utf-8"))
        self.socket.sendall(encrypted_packet)

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
            # client and server in lockstep
            # so its "safe" to pick single "message" from stream which actually
            # does not contain messages since there are no message start/end
            # delimeters due to lockstepping being good enough
            message = loads(packet.decode("utf-8"))
            if "arg" in message: # sending back and answer to an argument
                argument = message["arg"]
                exec(self.task + f"\n\nx = task({argument})") # <-wick'd smaht
                task_result = locals()['x'] # <-wick'd smaht
                message = {"arg": argument, "ans": task_result}
                self.send_json_message(message)
            elif "task" in message: # sending back ok since task was received
                self.task = message["task"]
                message = {"task": "ok"}
                self.send_json_message(message)
                print("Received and digested task. Ack sent.")
            elif "kill" in message:
                print("Server requested killing this worker :(")
                break

def main():
    #_ = system("cls||clear")
    worker = Worker("192.168.1.70")
    worker.start()



if __name__ == "__main__":
    main()
