#!/usr/bin/python3

"""
This file is provided as a demonstration tool for using pystributor
"""

from os import system
from pystributor_lib.pystributor import Hub, Worker
from time import perf_counter
import multiprocessing

def main():
    print("This python file is provided as a demo which uses pystributor to")
    print("perform an example task. Different systems will have different")
    print("performance characteristics. This will affect much performance")
    print("can be gained by using pystributor. Certain tasks will perform")
    print("worse with pystributor due to increased overhead.")
    print()
    print("If you test your own tasks, the most benefit will likely be")
    print("gained for tasks that have a moderate amount of argument sets to")
    print("distribute (in order of 100s or 1000s). Each argument should")
    print("be maximally CPU intensive when processed on worker.")
    print("")
    print("You should take a look inside this demo after trying it out.")
    print("")
    print("")
    print("")

    while True:
        inp = input("Enter H to start a hub from this demo. Enter W to start worker(s) on this PC: ")
        if inp == "H":
            ##### THIS STUFF HERE IS WHAT YOUR MAGICAL PROJECT SHOULD GIVE AS ARGUMENT
            ##### TO PYSTRIBUTOR VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
            # allways name the task function as task. Do what you want on the inside.
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
            args = [(i,) for i in range(10**8, (10**8)+200)]
            ##### THIS STUFF HERE IS WHAT YOUR MAGICAL PROJECT SHOULD GIVE AS ARGUMENT
            ##### TO PYSTRIBUTOR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

            while True:
                worker_count = input("Please enter worker count for pool: ")
                try:
                    worker_count = int(worker_count)
                    if worker_count <= 0:
                        continue
                except ValueError:
                    pass
                else:
                    break

            hub = Hub(task, args, poolsize=worker_count)


            timestamp = perf_counter()
            hub.start() # this blocks until answersheet is done
            print("Aikaa meni:", perf_counter()-timestamp)

            #print(hub.answersheet)
            break
        if inp == "W":
            while True:
                worker_count = input("Please enter nubmer of workers you want to create: ")
                try:
                    worker_count = int(worker_count)
                    if worker_count <= 0:
                        continue
                except ValueError:
                    pass
                else:
                    break

            def _worker_helper():
                worker = Worker()
                worker.start()

            worker_processes = []
            import os
            print(os.name)
            if os.name == 'nt':
                multiprocessing.set_start_method('spawn')
            
            for i in range(worker_count): # spawn multiple worker processes
                process = multiprocessing.Process(target=_worker_helper)
                worker_processes.append(process)
                process.start()
                #from time import sleep;sleep(1)
            for worker in worker_processes: # wait until they are doned
                worker.join()
            break

        else:
            continue


if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    main()





# TÖYT TÄHÄN ASTI: 24H PER NASSU
# ja makelle ehkä 10h lisää
# ja patrikille 4h