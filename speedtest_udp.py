from datetime import datetime, timedelta
from speedtest import SpeedTest
from socket import timeout, SOCK_DGRAM
from time import sleep

TAMANHO_PACOTE = 500

class SpeedTestUDP(SpeedTest):
    CONFIRMATION_PACKET = b"\x01" # = 1

    def __init__(self, listen_address, connect_address, port, role):
        super().__init__(listen_address, connect_address, port, role, SOCK_DGRAM)
    
    def receive(self):
        received_bytes = 0
        transmitted_bytes = 0
        packet = b'nao vazio'

        print("iniciando recebimento")
        self.connection.settimeout(5)  # Define um timeout de 5 segundos
        try:
            # Um pacote vazio indica o fim da transmissão de dados.
            while packet != self.EMPTY_PACKET:
                packet, _ = self.connection.recvfrom(self.PACKET_SIZE)
                received_bytes += len(packet)
                
            # remove o pacote vazio da contagem
            received_bytes-= len(packet)

            transmitted_bytes, _ = self.connection.recvfrom(self.INT_BYTE_SIZE)
            transmitted_bytes = int.from_bytes(transmitted_bytes, "big", signed=False)

            # sleep(3)
            # Envia o total salvo        
            stats = received_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
            self.connection.send(stats,self.connect_address)
        
        except timeout:
            self.connection.send(self.EMPTY_PACKET)
            print("Erro: Tempo de resposta excedido ao tentar receber o pacote")
    
        print("recebimento completo")
        self.results(transmitted_bytes, received_bytes)



    def send(self):
        end_time = datetime.now() + timedelta(seconds=self.DURATION)
        transmitted_bytes = 0
        received_bytes = 0  # Inicializando para evitar o UnboundLocalError

        print("iniciando envio...")
        self.connection.settimeout(5)  # Define um timeout de 5 segundos
        try:
            while datetime.now() < end_time:
                self.connection.send(self.data, self.connect_address)
                transmitted_bytes += len(self.data)

            self.connection.send(self.EMPTY_PACKET, self.connect_address)

            try:
                stats_packet = transmitted_bytes.to_bytes(self.INT_BYTE_SIZE, "big", signed=False)
                self.connection.send(stats_packet, self.connect_address)
            
                
            
            except timeout:
                print("Erro: Tempo de resposta excedido ao tentar receber o pacote")

            while received_bytes==0:
                    received_packet, _ = self.connection.recvfrom(self.INT_BYTE_SIZE)
                    received_bytes = int.from_bytes(received_packet, "big", signed=False)

        except ConnectionResetError as e:
            print(f"Erro de conexão: {e}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

        finally:
            print("envio completo")
            self.results(transmitted_bytes, received_bytes)

