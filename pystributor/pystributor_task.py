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