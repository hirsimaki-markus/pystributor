#Hub - responsible for managing the workers
from time import sleep
from os import system
from time import time
import socket
import threading
from cryptography import fernet
from Worker import Worker
from json import loads, dumps
from cryptography.fernet import Fernet
from inspect import getsource
from textwrap import dedent

class Hub:
    def __init__(self, task, args, poolsize=1, keep_pool_alive=True, host="0.0.0.0", port=1337, buff_size=4096, fernetkey="xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="):
        self.task = dedent(task)
        self.args = args
        self.host = host
        self.port = port
        self.buff_size = buff_size
        self.fernetkey = fernetkey
        self.answersheet = {}
        self.poolsize = poolsize
        self.pool = []
        self.keep_pool_alive = keep_pool_alive #Don't close the worker processes after calculations are done

        self.socket = None # initialized on socket startup
        self.fernet = None # initialized on socket startup
        self.total_time = None #given by super calculator when all finished

    def initialize_fernet(self):
        self.fernet = Fernet(self.fernetkey)
    
    def initialize_server_socket(self):
        """Returns a configured socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print("Socket initialized. Listening on adress:", self.host, ", port",  self.port)

    def _recvall(self, connection):
        """Receive all data from socket. Detects EOF. Worker and hub in lockstep."""
        accum = b''
        # the packets sent must be json so they end in } otherwise error checking wont work
        # TODO: prefix messages with their lenght. make recv buffer bigger.

        while True:
            part = connection.recv(self.buff_size)
            #print("APUUAAAAAAAA!!!!!"*100)
            """try:
                part = socket.recv(buff_size)
            except BlockingIOError:
                # blockin happens if nothing to read and last message len == buffer
                # so it keeps waiting for next packet even tho nothing is coming
                break
                # this continue should never happen. selector told connection is ready to read
                # we can reasonably expect that the whole "packet" has already been received
                # in timely manner before timeout should happen. this means that connection somehow failed
                # or the data being sent over the stream is extremely large or is being split into small
                # chunks and being slowed down too much by some network device"""
            accum += part
            if len(part) < self.buff_size:
                break # part was 0 or part was last
        return accum

    def manage_worker_thread(self, worker):
        connection = worker.connection
        message = {"task": self.task}
        self.send_json(message, worker.connection)
        while True:
            try:
                #data = connection.recv(self.buff_size)
                data = self._recvall(connection)
                if not data:
                    print("No data received.")
                    print(f"Worker {worker.id_number} is probably dead.")
                    connection.close
                    self.pool.remove(worker)
                    break
                worker.last_answer = time()
                self.parse_messages(data, worker)
            except ConnectionResetError:
                print(f"Worker {worker.id_number} is dead.")
                last_arguments = worker.arguments
                if last_arguments not in self.answersheet:
                    self.args.append((last_arguments, )) #TODO handle multiple arguments
                    print(f"Arguments {last_arguments} added back to arguments list to be processed")
                self.pool.remove(worker)
                print(f"Worker pool size is now {len(self.pool)}")
                break

        print("Worker listener thread finished.")

    def parse_messages(self, encrypted_data, pool_id):
        
        packet = self.fernet.decrypt(encrypted_data)
        message = loads(packet.decode("utf-8"))
        #print(f"New message from worker {pool_id.id_number}: {message}")
        if "ans" in message:
            pool_id.free = True
            arguments_used = message["arg"]
            answer = message["ans"]
            self.answersheet[arguments_used] = answer
        elif "alive" in message:
            pool_id.heartbeat = time()
            print(f"Worker {pool_id.id_number} is checked to be alive.")
        elif "task" in message:
            pool_id.free = True
        #elif "arg" in message: #Not used, slows down and we ca trust tcp
        #    if message["arg"] == "OK":
        #        pool_id.free = False

    def handle_new_workers(self):
        id = 0
        while True:
            print("Waiting for new workers to connect...")
            connection, address = self.socket.accept()
            print(f"Connected with a new worker {str(address)}")
            #TODO:Very bad numbering technique...do again
            id += 1
            worker_id = id
            print("Worker got id", worker_id)
            self.send_json({"id": worker_id}, connection)
            timestamp = time()
            self.pool.append(Worker(worker_id, connection, address, False, None, timestamp, timestamp))
            list_id = self.pool[-1]
            worker_thread = threading.Thread(target=self.manage_worker_thread, args=(list_id,))
            worker_thread.start()
            print(f"Worker {worker_id} added to the pool.")
            #sleep(1)

    def ping_workers(self):
        while True:
            sleep(60)
            print(self.answersheet)
            print(len(self.pool))
            if len(self.pool) > 0:
                for worker in self.pool:
                    if time() - worker.last_answer > 120: #TODO: Check heartbeat time vs last answer
                        self.send_json({"alive": "?"}, worker.connection)
                        print(f"Worker status: id{worker.id_number}, is free = {worker.free}, arguments = {worker.arguments}, heartbeat = {worker.heartbeat}, last answer = {worker.last_answer}.")

    def send_json(self, json_str, connection):
        packet = self.fernet.encrypt(dumps(json_str).encode("utf-8"))
        connection.sendall(packet)

    #def distribute_task(self):
    #    """Distribute task to workers"""
    #    for worker in self.pool:
    #        #connection, _address, _ready = worker
    #        task_str = self.get_task()
    #        message = {"task": task_str}
    #        worker.free = False
    #        self.send_json(message, worker.connection)

    #def get_task():
    #    """Returns task as a string so it can be distributed to workers"""
    #    from pystributor_task import task
    #    return getsource(task)

    #def get_args(self):
    #    """returns list of tuples to be distirbuted to workers as arguments"""
    #    from pystributor_args import args
    #    return args

    def super_calculator(self):
        """The brain which distributes tasks to workers in pool"""
        #distribute_task()
        number_of_arguments = len(self.args)
        self.total_time = time() #use the total time as start time for now
        while len(self.answersheet) < number_of_arguments:
            if len(self.args) != 0:
                while len(self.args) > 0:
                    for worker in self.pool: # until worker is found
                        if worker.free == False:
                            continue
                        argument = self.args.pop()
                        message = {"arg": argument[0]} # TODO: vararg support for n arguments
                        worker.free = False# set worker readiness to false
                        worker.arguments = argument[0]
                        self.send_json(message, worker.connection)
                        break
        print("Calculator done. All arguments distributed.")

    def start(self):
        print("Starting server...")
        self.initialize_fernet()
        self.initialize_server_socket()
        initial_connection_thread = threading.Thread(target=self.handle_new_workers)
        initial_connection_thread.setDaemon(True)
        initial_connection_thread.start()
        check_workers_thread = threading.Thread(target=self.ping_workers)
        check_workers_thread.setDaemon(True)
        check_workers_thread.start()
        print("Main entering while sleep")
        while(len(self.pool) < self.poolsize):
            print(f"Waiting for {self.poolsize - len(self.pool)} more workers to join the pool")
            sleep(5)
        print("Enough pool gathered. Starting calculations")
        arg_num = len(self.args)
        start_time = time()
        self.super_calculator()
        #while len(self.answersheet) < arg_num:
        #    sleep(0.1)
        self.total_time = time() - self.total_time
        print("Everything calculated. Total time:", self.total_time)
        if self.keep_pool_alive == False:
            for worker in self.pool:
                    if time() - worker.last_answer > 120: #TODO: Check heartbeat time vs last answer
                        self.send_json({"kill": "sorry"}, worker.connection)
            print("Sent shutdown messages to all workers")


def main():
    _ = system("cls||clear")
    input("The hub is usually used via import. Check demo.py for better example.\nPress enter to continue anyways and run a demo hub.\n")
    ##### THIS STUFF HERE IS WHAT YOUR MAGICAL PROJECT SHOULD GIVE AS ARGUMENT
    ##### TO PYSTRIBUTOR VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
    # allways name the task as task. do what you want on the inside.
    task = """
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
    # allways name th arguments args. should be list of tuples
    args = [(i,) for i in range(10**8, (10**8)+1000)]
    ##### THIS STUFF HERE IS WHAT YOUR MAGICAL PROJECT SHOULD GIVE AS ARGUMENT
    ##### TO PYSTRIBUTOR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    hub = Hub(task, args, 12, False)
    hub.start()
    print(len(hub.answersheet))
    print(hub.total_time)

if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    main()