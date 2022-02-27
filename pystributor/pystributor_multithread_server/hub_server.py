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

HOST = "0.0.0.0" #Accepting clients outside localhost requires this?
PORT = 6337
FERNET = Fernet("xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM=")
ANSWERSHEET = {}
#Setting up socket for connections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
worker_pool = []

#def report_worker_alive(worker):
    

def manage_worker_thread(list_id):
    connection = list_id.connection
    while True:
        data = connection.recv(1024)
        if not data:
            print("No data received.")
            print(f"Worker {list_id.id_number} is probably dead.")
            connection.close
            worker_pool.remove(list_id)
            break
        list_id.last_answer = time()
        parse_messages(data, list_id)

def parse_messages(encrypted_data, pool_id):
    
    packet = FERNET.decrypt(encrypted_data)
    message = loads(packet.decode("utf-8"))
    #print(f"New message from worker {pool_id.id_number}: {message}")
    if "ans" in message:
        pool_id.free = True
        question = message["param"]
        answer = message["ans"]
        ANSWERSHEET[question] = answer
    elif "alive" in message:
        pool_id.heartbeat = time()
        print(f"Worker {pool_id.id_number} is checked to be alive.")
    elif "task" in message:
        pool_id.free = True
    elif "arg" in message:
        if message["arg"] == "OK":
            pool_id.free = False

def handle_new_workers():
    id = 0
    while True:
        print("Waiting for new workers to connect...")
        connection, address = server.accept()
        print(f"Connected with a new worker {str(address)}")
        #TODO:Very bad numbering technique...do again
        id += 1
        worker_id = id
        print("Worker got id", worker_id)
        msg = "Your name is: " + str(worker_id)
        connection.send(msg.encode("utf_8"))
        msg = connection.recv(1024).decode("utf_8")
        timestamp = time()
        print(msg)
        worker_pool.append(Worker(worker_id, connection, address, True, None, timestamp, timestamp))
        list_id = worker_pool[-1]
        print(f"Worker {worker_id} added to the pool.")
        worker_thread = threading.Thread(target=manage_worker_thread, args=(list_id,))
        worker_thread.start()
        #sleep(1)

def ping_workers():
    while True:
        sleep(60)
        print(ANSWERSHEET)
        print(len(worker_pool))
        if len(worker_pool) > 0:
            for worker in worker_pool:
                send_json({"alive": "?"}, worker.connection)
                print(f"Worker status: id{worker.id_number}, is free = {worker.free}, arguments = {worker.arguments}, heartbeat = {worker.heartbeat}, last answer = {worker.last_answer}.")

def send_json(json_str, connection):
    packet = FERNET.encrypt(dumps(json_str).encode("utf-8"))
    connection.sendall(packet)

def distribute_task():
    """Distribute task to workers"""
    for worker in worker_pool:
        #connection, _address, _ready = worker
        task_str = get_task()
        message = {"task": task_str}
        worker.free = False
        send_json(message, worker.connection)

def get_task():
    """Returns task as a string so it can be distributed to workers"""
    from pystributor_task import task
    return getsource(task)

def get_args():
    """returns list of tuples to be distirbuted to workers as arguments"""
    from pystributor_args import args
    return args

def super_calculator(arguments_for_workers):
    """The brain which distributes tasks to workers in pool"""
    distribute_task()

    while len(arguments_for_workers) > 0:
        for worker in worker_pool: # until worker is found
            if worker.free == False:
                continue
            argument = arguments_for_workers.pop()
            message = {"arg": argument[0]} # TODO: vararg support for n arguments
            worker.free = False# worker readiness is false
            worker.arguments = argument[0]
            send_json(message, worker.connection)
            break
    print("Calculator done. All arguments distributed.")

def main(min_pool_size):
    print("Starting server...")
    initial_connection_thread = threading.Thread(target=handle_new_workers)
    initial_connection_thread.setDaemon(True)
    initial_connection_thread.start()
    check_workers_thread = threading.Thread(target=ping_workers)
    check_workers_thread.setDaemon(True)
    check_workers_thread.start()
    print("Main entering while sleep")
    while(len(worker_pool) < min_pool_size):
        sleep(5)
    print("Enough pool gathered. Starting calculations")
    arguments_for_workers = get_args()
    arg_num = len(arguments_for_workers)
    start_time = time()
    super_calculator(arguments_for_workers)
    while arg_num < len(ANSWERSHEET):
        sleep(0.5)
        print(arg_num)
        print(len(ANSWERSHEET))
    print("Everything calculated. Total time:", str(time()-start_time))
    #print(ANSWERSHEET)

if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    main(6)