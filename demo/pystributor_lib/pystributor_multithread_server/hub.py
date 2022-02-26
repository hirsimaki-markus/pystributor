#Hub - responsible for managing the workers
from time import sleep
import socket
import threading
from cryptography import fernet

HOST = "0.0.0.0" #Accepting clients outside localhost requires this?
PORT = 6337

#Setting up socket for connections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
worker_addresses = []
worker_names = []
worker_free = []

def manage_worker_thread(worker):
    while True:
        data = worker.recv(1024)
        if not data:
            print("No data received.")
            print(f"{worker} is probably dead.")
            worker_index = worker_addresses.index(worker)
            worker_names.remove(worker_names[worker_index])
            worker_free.remove(worker_free[worker_index])
            worker_addresses.remove(worker)
            worker.close()
            break
        #TODO: handle message
        print(data.decode("utf-8"))

def handle_new_workers():
    while True:
        print("Waiting for new workers to connect...")
        worker, address = server.accept()
        print(f"Connected with new worker {str(address)}")
        #Very bad numbering technique...do again
        worker_name = "Worker " + str(len(worker_addresses)+1)
        print(worker_name)
        msg = "Your name is: " + worker_name
        worker.send(msg.encode("utf_8"))
        msg = worker.recv(1024).decode("utf_8")
        print(msg)
        worker_names.append(worker_name)
        worker_addresses.append(worker)
        worker_free.append(True)
        print(f"{worker_name} added to the pool.")
        worker_thread = threading.Thread(target=manage_worker_thread, args=(worker,))
        worker_thread.start()

def ping_workers(workers):
    while True:
        sleep(30)
        print(len(worker_addresses))
        if len(workers) > 0:
            for worker in workers:
                worker.send(("Alive?").encode("utf_8"))
                data = worker.recv(1024).decode("utf_8")
                if data != "Yes.":
                    print("Worker dead.")
                if data == "Yes.":
                    print(f"{worker} is still alive.")

def main():
    initial_connection_thread = threading.Thread(target=handle_new_workers)
    initial_connection_thread.start()
    check_workers_thread = threading.Thread(target=ping_workers, args=(worker_addresses,))
    check_workers_thread.start()
    print("sdfsdfsdf")

if __name__ == "__main__":
    main()