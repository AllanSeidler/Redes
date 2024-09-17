from datetime import datetime, timedelta
from speedtest import SpeedTest
from socket import SOCK_STREAM

class SpeedTestTCP(SpeedTest):

    def __init__(self, listen_address, connect_address, port, role):
        super().__init__(listen_address, connect_address, port, role, SOCK_STREAM)

    def receive(self):
        received_bytes = 0
        packet = b""

        while packet!=self.EMPTY_PACKET:
            packet = self.recvall(self.connection, self.PACKET_SIZE)
            received_bytes += len(packet)
            
         # Envia o total salvo.
        stats = received_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
        self.connection.sendall(stats)

        transmitted_bytes = self.recvall(self.connection, self.INT_BYTE_SIZE)
        transmitted_bytes = int.from_bytes(transmitted_bytes, "big", signed=False)

        self.results(transmitted_bytes, received_bytes)

    
    def send(self):
        self.connection.listen()
        client, _ = self.connection.accept()
        
        end_time = datetime.now() + timedelta(seconds=self.RUN_DURATION)
        while datetime.now() < end_time:
            client.sendall(self.data)
            transmitted_bytes += len(self.data)
        
        client.sendall(self.EMPTY_PACKET)

        received_bytes = self.recvall(client, self.INT_BYTE_SIZE)
        received_bytes = int.from_bytes(received_bytes, "big", signed=False)

        stats = transmitted_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
        client.sendall(stats)

        self.results(transmitted_bytes, received_bytes)

