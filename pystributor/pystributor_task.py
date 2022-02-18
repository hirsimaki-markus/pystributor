#!/usr/bin/python3


"""
Usage: define your task in a way that can be passed to task() function. see
trivial is_prime for example.
"""



def is_prime(number):
    if number <= 1:
        return False
    for i in range(2, number):
        if (number % i) == 0:
            return False
    return True


task = is_prime