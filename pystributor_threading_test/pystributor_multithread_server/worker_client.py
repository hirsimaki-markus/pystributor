from asyncio import Task
import threading
from os import system
import socket
from cryptography import fernet
from time import sleep
from json import loads, dumps
from cryptography.fernet import Fernet

HOST = "127.0.0.1"
PORT = 6337
FERNET = Fernet("xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM=")

worker_name = "Unnamed worker :("
server_died_suddenly = False
server_requesting_shutdown = False
kill_threads = False

TASK = "Empty"

def recvall_worker(socket):
    """Receive all data from socket. Detects EOF. Worker and hub in lockstep."""
    accum = b''
    buff_size = 2048

    # the packets sent must be json so they end in } otherwise error checking wont work
    # TODO: prefix messages with their lenght. make recv buffer bigger.

    while True:
        part = socket.recv(buff_size)
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
        if len(part) < buff_size:
            break # part was 0 or part was last
    print(accum)
    return accum

def worker_receive_thread(worker):
    print("Receive thread started!")
    global server_died_suddenly
    global server_requesting_shutdown
    global kill_threads
    while True:
        if kill_threads == True:
            worker.close()
            break
        try:
            data = worker.recv(1024)
        except ConnectionResetError:
            print("Got connection reset error... shutting down connections")
            worker.close()
            server_died_suddenly = True
            kill_threads = True
            break
        if not data:
            print("Server hub closed socket... closing connections from this side")
            worker.close()
            server_died_suddenly = True
            kill_threads = True
            break
        parse_messages(data, worker)
    worker.close()
    print("Worker thread finished!")

def parse_messages(encrypted_data, connection):
    global TASK
    packet = FERNET.decrypt(encrypted_data)
    #print("New message from server:", packet)
    message = loads(packet.decode("utf-8"))
    if "arg" in message:
        #print("received arg")
        argument = message["arg"]
        #print(argument)
        send_json_message({"arg": "OK"}, connection)
        calculate_thread = threading.Thread(target=processing_thread, args=(argument, connection))
        calculate_thread.start()
        #task_result = task(argument)
        #send_json_message({"arg": argument, "ans": task_result})

    elif "alive" in message:
        send_json_message({"alive": "yes"}, connection)

    elif "task" in message:
        
        TASK = message["task"]
        print(TASK)
        send_json_message({"task": "ok"}, connection)
        print("Received and digested task. Ack sent.")

    elif "id" in message:
        global worker_name 
        worker_name = message["id"]
        print(f"I got an id: Worker {worker_name}")
    elif "kill" in message:
        global server_requesting_shutdown
        server_requesting_shutdown = True
        print("Server requested killing this worker :(")

def send_json_message(json_str, connection):
    packet = FERNET.encrypt(dumps(json_str).encode("utf-8"))
    connection.sendall(packet)

def worker_send_thread(worker):
    print("Sender thread started!")
    global kill_threads
    global server_died_suddenly
    while server_died_suddenly == False:
        if kill_threads == True:
            worker.close()
            break
        message = f"Hello it's me, Worker {worker_name} again..."
        try:
            worker.send(message.encode("utf_8"))
        except ConnectionResetError:
            print("Got connection reset error... shutting down connections")
            server_died_suddenly = True
            kill_threads = True
            worker.close()
            break
        sleep(10)
    print("Send thread finished!")

def initialize_connections():
    global kill_threads
    connection_succesful = False
    worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while connection_succesful == False:
        try:
            worker.connect((HOST, PORT))
            connection_succesful = True
            
        except Exception as e:
            print("Cannot connect to hub, trying again in 10 seconds.")
            #print(e)
            sleep(10)
    """while True:
        message = worker.recv(1024).decode("utf_8")
        if "Your name is:" in message:
            global worker_name
            worker_name = message[14:]
            print(f"I got a name: {worker_name}")
            worker.send((f"{worker_name} is ready to work!").encode("utf_8"))
            break"""
    
    kill_threads = False
    receive_thread = threading.Thread(target=worker_receive_thread, args=(worker,))
    #send_thread = threading.Thread(target=worker_send_thread, args=(worker,))
    receive_thread.setDaemon(True)
    #send_thread.setDaemon(True)
    receive_thread.start()
    #send_thread.start()

#def task(arg):
 #   """Placeholder for task until proper task is define by digest_task()"""
  #  # not working yet!
   # return "No proper task is defined yet!"

def task(number):
    return "Task Not Defined"


def processing_thread(arguments, connection):
    #print("Starting processing")
    answer = task(arguments)
    exec(TASK + f"x = task({arguments})")
    answer = locals()['x']
    send_json_message({"ans": answer, "param": arguments}, connection)
    #print("Answer sent. Exiting thread")



def main():
    print("Worker starting...")
    global server_died_suddenly
    global server_requesting_shutdown
    initialize_connections()
    while True:
        sleep(5)
        if server_died_suddenly == True:
            sleep(5) 
            server_died_suddenly = False
            initialize_connections()
        if server_requesting_shutdown == True:
            exit()
    

if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    main()