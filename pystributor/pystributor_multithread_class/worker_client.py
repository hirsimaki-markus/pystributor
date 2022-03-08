import threading
from os import system
import socket
from cryptography import fernet
from time import sleep
from json import loads, dumps
from cryptography.fernet import Fernet

worker_name = "Unnamed worker :("
server_died_suddenly = False
server_requesting_shutdown = False
kill_threads = False

class Worker:
    def __init__(self, host="127.0.0.1", port=1337, buff_size=4096, fernetkey="xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="):
        self.host = host
        self.port = port
        self.buff_size = buff_size
        self.fernetkey = fernetkey

        self.socket = None # initialized on socket startup
        self.fernet = None # initialized on socket startup
        self.task = None # initialized when hub provides a task
        self.keepalive = True
        self.serverdied = False
        self.kill_threads = False
    
    def initialize_fernet(self):
        self.fernet = Fernet(self.fernetkey)

    def recvall_worker(self):
        """Receive all data from socket. Detects EOF. Worker and hub in lockstep."""
        accum = b''
        # the packets sent must be json so they end in } otherwise error checking wont work
        # TODO: prefix messages with their lenght. make recv buffer bigger.

        while True:
            part = self.socket.recv(self.buff_size)
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

    def worker_receive_thread(self):
        print("Receive thread started!")
        while True:
            if self.kill_threads == True:
                self.socket.close()
                break
            try:
                #data = self.socket.recv(self.buff_size)
                data = self.recvall_worker()
            except ConnectionResetError:
                print("Got connection reset error... shutting down connections")
                self.socket.close()
                self.serverdied = True
                self.kill_threads = True
                break
            if not data:
                print("Server hub closed socket... closing connections from this side")
                self.socket.close()
                self.serverdied = True
                self.kill_threads = True
                break
            self.parse_messages(data) #Decides what to do with the message
        self.socket.close()
        print("Worker receive thread finished!")

    def parse_messages(self, encrypted_data):
        packet = self.fernet.decrypt(encrypted_data)
        #print("New message from server:", packet)
        message = loads(packet.decode("utf-8"))
        if "arg" in message:
            argument = message["arg"]
            #self.send_json_message({"arg": "OK"})
            calculate_thread = threading.Thread(target=self.processing_thread, args=(argument, ))
            calculate_thread.start()

        elif "alive" in message:
            self.send_json_message({"alive": "yes"})

        elif "task" in message:
            self.task = message["task"]
            print(self.task)
            self.send_json_message({"task": "ok"})
            print("Received and digested task. Ack sent.")

        elif "id" in message:
            global worker_name 
            worker_name = message["id"]
            print(f"I got an id: Worker {worker_name}")
        elif "kill" in message:
            self.keepalive = False
            print("Server requested killing this worker :(")

    def send_json_message(self, json_str):
        packet = self.fernet.encrypt(dumps(json_str).encode("utf-8"))
        self.socket.sendall(packet)

    def worker_send_thread(self):
        print("Sender thread started!")

        while self.serverdied == False:
            if self.kill_threads == True:
                self.socket.close()
                break
            message = f"Hello it's me, Worker {worker_name} again..."
            try:
                self.socket.sendall(message.encode("utf_8"))
            except ConnectionResetError:
                print("Got connection reset error... shutting down connections")
                self.serverdied = True
                self.kill_threads = True
                self.socket.close()
                break
            sleep(10)
        print("Send thread finished!")

    def initialize_connections(self):
        connection_succesful = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while connection_succesful == False:
            try:
                self.socket.connect((self.host, self.port))
                connection_succesful = True
                
            except ConnectionRefusedError:
                print("Cannot connect to hub yet, trying again in 1 second.")
                sleep(5)
        """while True:
            message = worker.recv(1024).decode("utf_8")
            if "Your name is:" in message:
                global worker_name
                worker_name = message[14:]
                print(f"I got a name: {worker_name}")
                worker.send((f"{worker_name} is ready to work!").encode("utf_8"))
                break"""
        
        self.kill_threads = False
        receive_thread = threading.Thread(target=self.worker_receive_thread)
        #send_thread = threading.Thread(target=worker_send_thread, args=(worker,))
        receive_thread.setDaemon(True)
        #send_thread.setDaemon(True)
        receive_thread.start()
        #send_thread.start()

    #def task(arg):
    #   """Placeholder for task until proper task is define by digest_task()"""
    #  # not working yet!
    # return "No proper task is defined yet!"

    #def task(self, number):
    #    return "Task Not Defined"


    def processing_thread(self, arguments):
        #print("Starting processing")
        #answer = self.task(arguments)
        exec(self.task + f"\n\nx = task({arguments})")
        answer = locals()['x']
        self.send_json_message({"ans": answer, "arg": arguments})
        #print("Answer sent. Exiting thread")



    def start(self):
        print("Worker starting...")
        self.initialize_fernet()
        self.initialize_connections()
        while True:
            sleep(5)
            if self.keepalive == False:
                exit()
            if self.serverdied == True:
                sleep(5) 
                self.serverdied = False
                self.initialize_connections()
            
    
def main():
    _ = system("cls||clear")
    print("Starting a standalone worker.")
    worker = Worker()
    worker.start()
    

if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    main()