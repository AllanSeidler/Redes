
import enum

class Roles(enum): SENDER=1,RECEIVER=2


class SpeedTest():
    def __init__(self,address,port,role):
        self.address = address
        self.port = port
        self.role = role


    def execute_role(self):
        if(self.role==Roles.SENDER):
            self.send()
        elif(self.role==Roles.RECEIVER):
            self.receive()
        else:
            print("Role indefinida!")


    def result():
        pass


    def send():
        pass


    def receive():
        pass


