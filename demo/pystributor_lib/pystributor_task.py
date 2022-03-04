"""
worker task is defined with functions bound to task variable. see trivial example with is_prime()
"""



def task(number):
    """Define your task here. is_prime is provided as an example task."""
    def is_prime(number):
        #from time import sleep
        #sleep(2)
        if number <= 1:
            return False
        for i in range(2, number):
            if (number % i) == 0:
                return False
        return True
    return is_prime(number)



if __name__ == "__main__":
    from os import system
    _ = system("cls||clear") # clear screen on windows and unix
    args = [(i,) for i in range(10**8, (10**8)+200)]
    print("starting test by running task without pystributor...")

    from time import perf_counter
    alku = perf_counter()

    for i in args:
        task(i[0])

    print("kesto:", perf_counter()-alku)