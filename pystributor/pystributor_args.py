"""
task arguments defined with any python object that can be converted to list of tuples.
tuples are used to support multipe arguments. see get_numbers() for example.
"""



def get_numbers():
    """Returns list of 20 tuples, each containing a number. Runs from 1 to 20
    assigning a list with hard coded items to args would also work.
    """
    accum = []
    for i in range(10**2, (10**2)+1000):
        accum.append((i,))
    return accum


args = get_numbers() # get_numbes() could also be hard coded list here

