from datetime import datetime, timedelta
from speedtest import SpeedTest
from socket import timeout, SOCK_DGRAM

TAMANHO_PACOTE = 500

class SpeedTestUDP(SpeedTest):
    CONFIRMATION_PACKET = b"\x01" # = 1

    def __init__(self, listen_address, connect_address, port, role):
        super().__init__(listen_address, connect_address, port, role, SOCK_DGRAM)
    
    def receive(self):
        received_bytes = 0
        packet = b'nao vazio'

        print("iniciando recebimento")

        # Um pacote vazio indica o fim da transmissão de dados.
        while packet != self.EMPTY_PACKET:
            packet, _ = self.connection.recvfrom(self.PACKET_SIZE)
            received_bytes += len(packet)
            
        
        # Envia o total salvo
        stats = received_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
        self.connection.sendto(stats,self.connect_address)
        
        transmitted_bytes, _ = self.connection.recvfrom(self.INT_BYTE_SIZE)
        transmitted_bytes = int.from_bytes(transmitted_bytes, "big", signed=False)

        print("recebimento completo")
        self.results(transmitted_bytes, received_bytes)



    def send(self):
        end_time = datetime.now() + timedelta(seconds=self.DURATION)
        transmitted_bytes = 0

        print("iniciando envio")
        try:
            while datetime.now() < end_time:
                self.connection.sendto(self.data,self.connect_address)
                transmitted_bytes += len(self.data)

            
            received_bytes = 0        
            self.connection.sendto(self.EMPTY_PACKET,self.connect_address)

            received_packet, _ = self.connection.recvfrom(self.INT_BYTE_SIZE)
            received_bytes = int.from_bytes(received_packet, "big", signed=False)
            print("parando aqui")
            stats_packet = transmitted_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
            self.connection.sendto(stats_packet,self.connect_address)

        finally:
            print("envio completo")
            self.results(transmitted_bytes, received_bytes)

