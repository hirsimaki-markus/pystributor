import threading
import socket
from cryptography import fernet
from time import sleep

HOST = "127.0.0.1"
PORT = 6337

worker_name = "Unnamed worker :("
server_died_suddenly = False
server_requesting_shutdown = False
kill_threads = False


def worker_receive_thread(worker):
    global server_died_suddenly
    global server_requesting_shutdown
    global kill_threads
    while True:
        if kill_threads == True:
            worker.close()
            break
        data = worker.recv(1024)
        if not data:
            worker.close()
            server_died_suddenly = True
            kill_threads = True
            break
        data = data.decode("utf_8")
        if data == "Alive?":
            worker.send("Yes.".encode("utf_8"))
        if data == "Kill worker.":
            server_requesting_shutdown = True
        
        print(f"New message from server: {data}")
    print("Worker thread finished!")

def worker_send_thread(worker):
    global kill_threads
    while True:
        if kill_threads == True:
            worker.close()
            break
        message = f"Hello it's me, {worker_name} again..."
        worker.send(message.encode("utf_8"))
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
            print(e)
            sleep(10)
    while True:
        message = worker.recv(1024).decode("utf_8")
        if "Your name is:" in message:
            global worker_name
            worker_name = message[14:]
            print(f"I got a name: {worker_name}")
            worker.send((f"{worker_name} is ready to work!").encode("utf_8"))
            break
    
    kill_threads = False
    receive_thread = threading.Thread(target=worker_receive_thread, args=(worker,))
    send_thread = threading.Thread(target=worker_send_thread, args=(worker,))
    receive_thread.start()
    send_thread.start()

def main():
    global server_died_suddenly
    global server_requesting_shutdown
    initialize_connections()
    while True:
        sleep(5)
        if server_died_suddenly == True:
            server_died_suddenly = False
            initialize_connections()
        if server_requesting_shutdown == True:
            exit()
    

if __name__ == "__main__":
    main()