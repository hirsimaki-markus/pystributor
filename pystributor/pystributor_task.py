"""
worker task is defined with functions bound to task variable. see trivial example with is_prime()
"""



def is_prime(number):
    if number <= 1:
        return False
    for i in range(2, number):
        if (number % i) == 0:
            return False
    return True


task = is_prime
