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
    DURATION = 20  # Duração dos testes.
    INT_BYTE_SIZE = 8  # Tamanho da representação de um inteiro como bytes.
    PACKET_SIZE = 1024  # Tamanho de cada pacote. (1kb)
    EMPTY_PACKET = b"\x00" * PACKET_SIZE  # Pacote vazio indicando o fim da transmissão.

    def __init__(self, listen_address, connect_address, port, role, socket_type):
        self.listen_address = (listen_address, port)
        self.connect_address = (connect_address, port)
        self.role = role
        self.socket_type = socket_type
        self.connection = socket.socket(socket.AF_INET, socket_type.value)
        self.data = randbytes(self.PACKET_SIZE)

    def run(self):
        self.execute_role()
        self.swap_roles()
        self.execute_role()

    def swap_roles(self):
        self.role = Roles((self.role.value + 1) % 2)
        self.connection.close()
        self.connection = socket.socket(socket.AF_INET, self.socket_type.value)

    def execute_role(self):
        if self.role == Roles.SENDER:
            print(f"Executando de {self.connect_address}")
            sleep(1)
            self.connection.connect(self.connect_address)
            self.send()
        elif self.role == Roles.RECEIVER:
            sleep(2)
            self.connection.bind(self.listen_address)
            print(f"Aguardando conexão em {self.listen_address}")
            self.connection.listen(1)  # O receiver precisa ouvir conexões
            conn, addr = self.connection.accept()  # Aceitar a conexão
            print(f"Conexão estabelecida com {addr}")
            self.connection = conn  # Substituir o socket para a conexão aceita
        
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
    def results(transmitted_bytes, received_bytes):
        print(f'Bytes enviados: {transmitted_bytes}')
        print(f'Bytes recebidos: {received_bytes}')
        print(f'Tempo de execução: {SpeedTest.DURATION} (s)\n')

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def receive(self):
        pass