from os import system
from pystributor import Hub, Worker
from time import perf_counter
import multiprocessing as mp
import statistics


#General gudlines:
#Each condition run 2 times and average result recorded
#First cases are run with 1 to 24 local workers to find the optimal worker count.
#Then the optimal worker count test is run with a remote hub
#Then scalability is tested with adding remote workers optimally to multiple computers.

task_str = """
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


def get_args(case):
    #cases = [(1000, 10000), (10**6, 10**6+1000), (10**7, 10**7+1000), (10**8, (10**8)+1000), (10**9, (10**9)+1000)]
    cases = [(1, 100), (10**1, 10**1+100), (10**2, 10**2+100), (10**3, (10**3)+100), (10**4, (10**4)+100)]
    start, end = cases[case]
    return [(i,) for i in range(start, end)]

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

def bare_function(case):
    args = get_args(case)
    timestamp = perf_counter()
    for i in args:
        task(i[0])
    timestamp = perf_counter() - timestamp
    print("Aikaa meni:", timestamp)
    return timestamp

def run_average_2_for_base(case_number):
    timings = []
    averages = []
    timings.append(bare_function(case_number))
    timings.append(bare_function(case_number))

    print(timings)
    average = statistics.fmean(timings)
    averages.append(average)
    print(f"Avarage time with case {case_number} was: {average}")
    return averages

def run_all_bare_function_cases():
    bare_function_times = []
    for i in range(5):
        time = run_average_2_for_base(i)
        bare_function_times.append(f"Case {i}", time)
    return bare_function_times
    

def local_workers(worker_num, case):
    workers = []
    for i in range(worker_num):
        worker = mp.Process(target=_worker_helper)
        workers.append(worker)
        worker.start()
        

    
    hub = Hub(task_str, get_args(case), worker_num)
    timestamp = perf_counter()
    hub.start() # this blocks until answersheet is done
    timestamp = perf_counter() - timestamp
    print("Aikaa meni:", timestamp)
    #for i in range(worker_num):
    #    i.join()
    return timestamp

def measure_local_workers():
    local_worker_times = []
    for worker_num in range(5):
        for case_num in range(5):
            time = local_workers(worker_num, case_num)
            local_worker_times.append(f"{worker_num} workers", f"Case {case_num}", time)
    return local_worker_times




def _worker_helper():
    worker = Worker()
    worker.start()

def main():
    bare_times = run_all_bare_function_cases()
    pystributor_times = measure_local_workers()
    print(bare_times)
    print(pystributor_times)

if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    mp.set_start_method('spawn') #set start to spawn to enable function on windows and linux
    main()