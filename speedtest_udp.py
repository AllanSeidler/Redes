from datetime import datetime, timedelta
from speedtest import SpeedTest
from socket import timeout, SOCK_DGRAM

TAMANHO_PACOTE = 500

class SpeedTestUDP(SpeedTest):
    CONFIRMATION_PACKET = b"\x01" # = 1

    def __init__(self, listen_address, connect_address, port, role):
        super().__init__(listen_address, connect_address, port, role, SOCK_DGRAM)
    
    def receive(self):
        self.connection.settimeout(1)
        received_bytes = 0

        while True:
            try:
                packet = self.recvall(self.connection, self.PACKET_SIZE)
                # Um pacote vazio indica o fim da transmissão de dados.
                if packet == self.EMPTY_PACKET:
                    break
                received_bytes += len(packet)

            except timeout:
                # Um pacote vazio para indicar que está pronto para receber os dados
                self.connection.send(self.EMPTY_PACKET) 
            
        # Envia o total salvo
        status = b'\x00' # status = 0
        while status!=self.CONFIRMATION_PACKET:
            try:
                stats = received_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
                self.connection.send(stats)

                transmitted_bytes = self.connection.recv(self.INT_BYTE_SIZE)
                transmitted_bytes = int.from_bytes(transmitted_bytes, "big", signed=False)

                status = self.connection.recv(self.PACKET_SIZE)
                
            except timeout:
                pass

        self.results(transmitted_bytes, received_bytes)

    def send(self):
        _, address = self.connection.recvfrom(self.PACKET_SIZE)
        end_time = datetime.now() + timedelta(seconds=self.RUN_DURATION)
        transmitted_bytes = 0

        while datetime.now() < end_time:
            self.connection.sendto(self.data, address)
            transmitted_bytes += len(self.data)

        self.connection.settimeout(1)
        received_bytes = 0
        while received_bytes == 0:
            try:
                self.connection.sendto(self.EMPTY_PACKET, address)

                received_packet = self.connection.recv(self.INT_BYTE_SIZE)
                received_bytes = int.from_bytes(received_packet, "big", signed=False)

                stats_packet = transmitted_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
                self.connection.sendto(stats_packet, address)

                self.connection.sendto(self.CONFIRMATION_PACKET, address)
            except timeout:
                pass

        self.connection.settimeout(0)

        self.results(transmitted_bytes, received_bytes)
