#!/usr/bin/python3

"""
This file is provided as a demonstration tool for using pystributor
"""

from pystributor.pystributor import Hub, Worker
from time import perf_counter
from os import system, name
import multiprocessing
from multiprocessing.managers import BaseManager

SAMPLE_ARGS = [(i,) for i in range(10**8, (10**8)+200)]
SAMPLE_TASK = """
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
        return _my_bad_prime_number_checker(my_argument)
"""

def _worker_helper():
    """This helper must be placed in this scope for windows compability"""
    worker = Worker()
    worker.start()

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
    print("You should take a look inside this demo file after trying it out.")
    print("")
    print("")
    print("")

    while True:
        print("Enter H to start a hub. Enter W to start worker(s)")
        print("(You will have to start at least two instances of this demo,")
        print("one for hub and one for workers)")
        inp = input(": ")
        if inp == "H":
            while True: # loop for valid input
                worker_count = input("Please enter how many worker connections to wait for: ")
                try:
                    worker_count = int(worker_count)
                    if worker_count <= 0:
                        continue
                except ValueError:
                    pass
                else:
                    break

            hub = Hub(SAMPLE_TASK, SAMPLE_ARGS, poolsize=worker_count)
            timestamp = perf_counter()
            hub.start() # this blocks until answersheet is done
            print("Time spent (including waiting for workers):", perf_counter()-timestamp)
            print("\nSelected excerpt from hub.answersheet:")
            print_counter = 0
            for arg, ans in hub.answersheet.items():
                if ans:
                    print(arg, "is prime.")
                    print_counter += 1
                    if print_counter >= 30:
                        break
            break
        if inp == "W":
            while True: # loop for valid input
                worker_count = input("Please enter the number of worker procsesses you want to create: ")
                try:
                    worker_count = int(worker_count)
                    if worker_count <= 0:
                        continue
                except ValueError:
                    pass
                else:
                    break



            worker_processes = []


            while True: # likanen tunkki. 5 riviä muutoksia tässä.
                for i in range(worker_count): # spawn multiple worker processes #!!!
                    process = multiprocessing.Process(target=_worker_helper) #!!!
                    worker_processes.append(process) #!!!
                    process.start() #!!!

                while True: # block until all workers done
                    from time import sleep
                    sleep(1)
                    if all([not i.is_alive() for i in worker_processes]):
                        break
            break # TÄMÄ PITÄÄ SÄILYTÄÄ #!!!!!
        else:
            continue


if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    multiprocessing.set_start_method('spawn')
    #if name == "nt":
    #    # windows compability. default is to fork in windows.
    #    multiprocessing.set_start_method("spawn")
    main()





# TÖYT TÄHÄN ASTI: 24H PER NASSU
# ja makelle ehkä 10h lisää
# ja patrikille 4h
# ja molemmille 4h
# ja patrikille 6h
# ja yhdessä 4h