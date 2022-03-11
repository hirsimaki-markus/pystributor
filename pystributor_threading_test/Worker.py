import re


class Worker:
    def __init__(self, connection, adress, status, arguments):
        self.conncetion = connection
        self.adress = adress
        self.status = status
        self.arguments = arguments
    
    def __init__(self, connection, adress, status):
        self.conncetion = connection
        self.adress = adress
        self.status = status
        self.arguments = None

    def __init__(self, connection, adress):
        self.conncetion = connection
        self.adress = adress
        self.status = None
        self.arguments = None

    def print_worker_info(self):
        print("Worker at address", self.adress, "has ready state of", self.status, "and has last got arguments", self.arguments)
    
    def getConnection(self):
        return self.conncetion
    
    def getAdress(self):
        return self.adress
    
    def getStatus(self):
        return self.status
    
    def getArguments(self):
        return self.arguments