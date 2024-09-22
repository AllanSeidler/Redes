from abc import ABCMeta, abstractmethod
from random import randbytes
from enum import Enum
from time import sleep
import socket
from socket import timeout


class Roles(Enum):
    SENDER = 0
    RECEIVER = 1


class SpeedTest(metaclass=ABCMeta):
    # Declaração das constantes
    DURATION = 1  # Duração dos testes.
    INT_BYTE_SIZE = 8  # Tamanho da representação de um inteiro como bytes.
    PACKET_SIZE = 1024  # Tamanho de cada pacote. (1kb)
    EMPTY_PACKET = b"\x00" * PACKET_SIZE  # Pacote vazio indicando o fim da transmissão.
    socket_to_str ={socket.SOCK_DGRAM:'UDP',socket.SOCK_STREAM:'TCP'}

    def __init__(self, listen_address, connect_address, port, role, socket_type):
        self.listen_address = (listen_address, port)
        self.connect_address = (connect_address, port)
        self.role = role
        self.socket_type = socket_type
        self.connection = socket.socket(socket.AF_INET, socket_type.value)
        self.data = randbytes(self.PACKET_SIZE)

    def run(self):
        print(f"Iniciando teste de conexão com socket {self.socket_to_str[self.socket_type]}")
        self.execute_role()
        self.swap_roles()
        self.execute_role()

    def swap_roles(self):
        self.role = Roles((self.role.value + 1) % 2)
        self.connection.close()
        self.connection = socket.socket(socket.AF_INET, self.socket_type.value)

    def execute_role(self):
        if self.role == Roles.SENDER:
            # print(f"Executando de {self.connect_address}")
            # sleep(1)
            self.connection.bind(self.listen_address)
            self.send()
            
        elif self.role == Roles.RECEIVER:
            # sleep(2)
            self.connection.connect(self.connect_address)
            # print(f"Aguardando conexão em {self.listen_address}")

            self.receive()
        else:
            print(f'Role de valor {self.role} inexistente.')

    @staticmethod
    def recvall(sock, size) :
        """ Recebe um número de bytes através de um socket. """
        message = b""
        while len(message) < size:
            try:
                buffer = sock.recv(size - len(message))
                message += buffer
            except timeout:
                pass
        return message


    @staticmethod
    def format_bytes(b) -> str:
        index = 0
        values = {0: "b", 1: "Kb", 2: "Mb", 3: "Gb", 4: "Tb"}
        while b > 1024 and index < 4:
            b /= 1024
            index += 1
        return f"{round(b, 2)} {values[index]}"

    
    def results(self,transmitted_bytes, received_bytes):
        lost_bytes = transmitted_bytes - received_bytes
        lost_packets = lost_bytes / SpeedTest.PACKET_SIZE

        packets_per_second = int(received_bytes / (SpeedTest.DURATION * SpeedTest.PACKET_SIZE))
        transmitted_bits_per_second = (received_bytes * 8) / SpeedTest.DURATION
        transmitted_bits_formated = SpeedTest.format_bytes(transmitted_bits_per_second)

        
        print(f"Role: {self.role.name}")
        print("Tamanho do header: 0 bytes")
        print(f"Tamanho do payload: {SpeedTest.PACKET_SIZE} bytes")
        print(f"Tempo de execução do teste: {SpeedTest.DURATION}s")
        print(f"Total de bytes transmitidos: {transmitted_bytes:,}")
        print(f"Taxa de transmissão de pacotes: {packets_per_second:,} p/s")
        print(f"Pacotes perdidos: {lost_packets:,}")
        print(f"Taxa de perda de pacotes: {round((lost_packets / transmitted_bytes ) * 100, 2)}%")
        print(f"Velocidade de {self.role}: {transmitted_bits_formated}/s")
        print('-------------------------------------------------\n')
        

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def receive(self):
        pass