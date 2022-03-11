class Worker:
    def __init__(self, id_number, connection, address, free, arguments, heartbeat, last_answer):
        self.id_number = id_number
        self.connection = connection
        self.address = address
        self.free = free
        self.arguments = arguments
        self.heartbeat = heartbeat
        self.last_answer = last_answer

    def print_worker_info(self):
        return "aasdfs"
        #print("Worker at address", self.adress, "has ready state of", self.status, "and has last got arguments", self.arguments)

    def Connection(self):
        return self.connection

    def Address(self):
        return self.address
    
    def Free(self):
        return self.free
    
    def Arguments(self):
        return self.arguments

    def Id(self):
        return self.id_number