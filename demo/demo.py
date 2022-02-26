#!/usr/bin/python3

"""
This file is provided as a demonstration tool for using pystributor
"""

from os import system
from pystributor.pystributor import hub



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
    input("")
    _ = input("Press enter to continue and start your very own hub: ")


    ##### THIS STUFF HERE IS WHAT YOUR MAGICAL PROJECT SHOULD GIVE AS ARGUMENT
    ##### TO PYSTRIBUTOR VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
    # allways name the task as task. do what you want on the inside.
    def task(my_argument):
        """When creating your own task, always name it task"""
        def _my_bad_prime_number_checker(number):
            """Returns true if prime, false otherwise"""
            if number <= 1:
                return False
            for i in range(2, number):
                if (number % i) == 0:
                    return False
            return True
        return _my_bad_prime_number_checker(my_argument)
    # allways name th arguments args. should be list of tuples
    args = [(i,) for i in range(10**6, (10**6)+500)]
    ##### THIS STUFF HERE IS WHAT YOUR MAGICAL PROJECT SHOULD GIVE AS ARGUMENT
    ##### TO PYSTRIBUTOR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


    hub(task,
        args,
        host="0.0.0.0",
        port=1337,
        buff_sisze=4096,
        fernetkey="xlHo5FYF1MuSHnvb_QJPWhEjOTCO5Ioennu_yJtQXYM="
    )




if __name__ == "__main__":
    _ = system("cls||clear") # clear screen on windows and unix
    main()





# TÖYT TÄHÄN ASTI: 18H PER NASSU
# ja makelle ehkä 3h lisää