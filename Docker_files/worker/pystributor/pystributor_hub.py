#!/usr/bin/python3


"""
Hub class is used to spawn hub objects for pystributor. Polling the results
from hub.answersheet is left to the end user if they are to be examined
during the operation of hub as it is blocking.

Important: worker pool data type is currently implemented as 2D list
[[connection, address, is_ready], [...], [...]]
The data should be accessed with list notation by enumerating worker pool if
needed.
"""

from socket import socket as system_socket, SHUT_RDWR
from selectors import DefaultSelector, EVENT_READ
from atexit import register as atexit_register
from cryptography.fernet import Fernet
from json import loads, dumps
from threading import Thread
from textwrap import dedent
from time import sleep
from time import time
from os import system

class Hub:
    def __init__(self, task, args, poolsize=1, host="0.0.0.0", port=1337, buff_size=4096, fernetkey="xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="):
        self.task = dedent(task)
        self.args = args
        self.host = host
        self.port = port
        self.buff_size = buff_size
        self.fernetkey = fernetkey
        self.answersheet = {}
        self.poolsize = poolsize

        self.socket = None # initialized on socket startup
        self.fernet = None # initialized on socket startup
        self.pool = None # initialized on socket startup
        self.t1 = None # initialized on socket startup
        self.t2 = None # initialized on socket startup
        self.total_time = None # given by super calculator when all finished

    def initialize_server_socket(self):
        """Returns a configured socket from os level"""
        socket = system_socket()
        socket.setblocking(False) # blocking would prevent ctrl+c on windows
        socket.bind((self.host, self.port))
        self.socket = socket
        print("Socket initialized. Listening on adress:", self.host, ", port",  self.port)

    def exit_handler(self):
        """Cleanly released socket back to os"""
        try:
            self.socket.shutdown(SHUT_RDWR)
        except OSError as e:
            if e.errno == 107:
                pass # socket already closed

    def initialize_fernet(self):
        """Fernet helper"""
        self.fernet = Fernet(self.fernetkey)

    def distribute_task(self):
        """Distribute task to workers"""
        for connection, _address, _ready in self.pool:
            #connection, _address, _ready = worker
            message = {"task": self.task}
            packet = self.fernet.encrypt(dumps(message).encode("utf-8"))
            # client and server in lockstep > can send single "message" to stream
            connection.sendall(packet)

    def _recvall_hub(self, connection):
        """Receive all data from connection. Detects EOF, not message delimeter.

        Worker and hub are in lockstep; currently no need for message start
        and end symbols. Safe to assume messages are received as intended.
        If features like heartbeat for workers are added this function needs
        updating
        """
        accum = b''
        # TODO: prefix messages with their lenght.
        while True:
            # this busy waiting is necessary or connections might be missed.
            # DO NOT add sleep here
            try:
                part = connection.recv(self.buff_size)
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

    def super_calculator(self):
        """The brain which distributes tasks to workers in pool"""
        print("Super calculator daemon online. Distributing tasks to workers.")
        self.distribute_task()
        class NestedLoopException(Exception):
            """raised to close nested loop"""
            pass
        arguments_for_workers = self.args
        self.total_time = time()
        for argument in arguments_for_workers: # for all arguments
            try:
                while True: # until argument is sent
                    for i, worker in enumerate(self.pool): # until worker found
                        connection, _address, ready = worker
                        if not ready:
                            continue
                        message = {"arg": argument[0]} # TODO: vararg support
                        packet = self.fernet.encrypt(dumps(message).encode("utf-8"))
                        connection.sendall(packet)
                        self.pool[i][2] = False # worker readiness is false
                        raise NestedLoopException
            except NestedLoopException:
                continue
        print("Calculator daemon done. All arguments distributed.")

    def listener(self):
        """Handles getting replies from workers"""
        print("Listener daemon online. Waiting for worker replies.")
        connection_selector = DefaultSelector()
        # selector can be queried for file descriptors waiting for I/O operations
        # one selector will handle up to 1024 workers
        # future work could include using threading multiple selectors.
        for i, worker in enumerate (self.pool):
            connection, _address, _ready = worker
            connection_selector.register(connection, EVENT_READ, i)
        def _selector_read_handler(connection, pool, worker_idx):
            """Handles data read by selector from connections"""
            encrypted_packet = self._recvall_hub(connection)
            if encrypted_packet: # if not empty
                packet = self.fernet.decrypt(encrypted_packet)
                message = loads(packet.decode("utf-8"))
                if "task" in message:
                    # task was received succesfully
                    if message["task"] == "ok":
                        self.pool[worker_idx][2] = True
                elif "ans" in message:
                    # received answer to a calculation
                    arguments = message["arg"]
                    answer = message["ans"]
                    self.pool[worker_idx][2] = True
                    self.answersheet[arguments] = answer
            else: # connection is likely closing since no data
                print("Closing worker connection. Worker dropped from pool.")
                connection_selector.unregister(connection)
                connection.close()
                # TODO: hub and worker still breaks if worker is dropped
                # at any point; maybe add graceful exit handling
        arg_count = len(self.args)
        while True:
            for selectorkey, mask in connection_selector.select():
                # select() call blocks.
                connection = selectorkey.fileobj
                worker_idx = selectorkey.data
                _selector_read_handler(connection, self.pool, worker_idx)
            if arg_count == len(self.answersheet):
                self.total_time = time() - self.total_time
                break
        print("Listener daemon done. All answers received.")

    def start_daemons(self):
        self.t1 = Thread(target=self.super_calculator, daemon=True)
        self.t2 = Thread(target=self.listener, daemon=True)
        self.t1.start()
        self.t2.start()

    def discover_workers(self):
        """Waits for workers to connect. Initializes worker pool when interrupted"""
        pool = []
        print("Building worker pool. Waiting for workers to come online.", end="")
        print(" Start workers now.\n")
        print("!!! Press <ctrl+c> to stop waiting for more workers to join !!!")
        if self.poolsize != 0:
            print("!!! Automatically stopping wait when", self.poolsize, "workers connected !!!")
        self.socket.listen(0) # backlog = 0
        try:
            while True:
                # sleep(0.1) # fix busy waiting
                try:
                    connection, address = self.socket.accept()
                except BlockingIOError:
                    # socket is set to nonblocking. error happens in loop
                    # this allows for ctrl+c to work also on windows
                    continue
                connection.setblocking(False) # must be nonblocking for selector
                pool.append([connection, address, None])
                # worker status is undefined None as it has not responded yet
                print("Added worker to pool. Worker address is", address[0] + ":"
                    + str(address[1]) + ".", "Pool size is now", len(pool), )
                if (self.poolsize != 0) and (len(pool) >= self.poolsize):
                    break
        except KeyboardInterrupt:
            print("\n\nDone building worker pool. Pool size:", len(pool))
        self.pool = pool

    def kill_workers(self):
        """Close connections for workers"""
        for i, worker in enumerate(self.pool):
            connection, _address, _sready = worker
            connection.close()
            self.pool[i][2] = False # worker readiness is false

    def start(self):
        self.initialize_server_socket()
        self.initialize_fernet()
        self.discover_workers()
        atexit_register(self.exit_handler)
        print("Hub initialized. Starting listener and calculator daemons.", end=" ")
        print("Waiting for daemons to finish.")
        self.start_daemons()

        while (self.t1.is_alive() or self.t2.is_alive()):
            # wait until all arguments have bee sent to workers and wait until
            # all arguments have been processed
            sleep(1)

        print("Daemons done. Killing workers.")
        self.kill_workers()
        self.socket.close()



def main():
    _ = system("cls||clear")
    print("You probably should not be running this file.")
    print("Press enter to continue anyways and run test hub. Use demo.py for better example.\n")
    input("")
    sample_task = """
    def task(my_argument):
        # When creating your own task, always name it task
        def _my_bad_prime_number_checker(number):
            # Returns true if prime, false otherwise
            if number <= 1:
                return False
            for i in range(2, number):
                if (number % i) == 0:
                    return False
            return True
        return _my_bad_prime_number_checker(my_argument)"""
    args = [(i,) for i in range(10**8, (10**8)+1000)]
    hub = Hub(sample_task, args)
    hub.start()
    print(hub.answersheet)
    print(len(hub.answersheet))
    print(hub.total_time)

if __name__ == "__main__":
    main()
