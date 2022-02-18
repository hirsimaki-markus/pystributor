"""
task arguments defined with any python object that can be converted to list of tuples.
see trivial example with list and generator
"""



def example_task_arguments():
    """Returns list of 20 tuples, each containing a number. Runs from 1 to 20"""
    num = 1
    while num < 21:
        yield (num,) # return tuples with size of one
        num += 1


args = list()
