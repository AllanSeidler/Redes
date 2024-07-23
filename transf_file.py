import socket
import json
import os
import math

class Servidor:
    def __init__(self, endereco, porta):
        self.endereco = endereco
        self.porta = porta
        self.conexao = None
        self.usuarios = []

    def start(self):
        self.conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexao.bind((endereco, porta))
        self.conexao.listen()
        print(f"Servidor escutando em {endereco}:{porta}")

class Cliente:
    def __init__(self, nome):
        self.nome = nome
        self.conexao = None
    
    def start(self, endereco, porta):
        self.conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexao.connect((endereco, porta))

class Pacote: 
    def __init__(self):
        separador = 'separador™'
        separador_pk = 'separador☺' 

    @staticmethod
    def encode(id,payload):
        header = f"{id}"
        packet = f"{header}{Pacote.separador}{payload}"
        checksum = hash(packet)
        packet = f"{packet}{Pacote.separador}{checksum}{Pacote.separador_pk}"
        binary_packet = packet.encode()
        return binary_packet
    
    @staticmethod
    def decode(binary_packet):
        packet = binary_packet.decode()
        packets = packet.split(Pacote.separador_pk)
        hpc = []
        for p in packets:
            hpc.append(p.split(Pacote.separador))
        return hpc


if __name__ == "__main__":
    endereco = input("Endereço do servidor: ")
    porta = int(input("Porta do servidor: "))
    tipo = int(input("Cliente(1) ou Servidor(2): "))

    if tipo==2:
        servidor = Servidor(endereco, porta)
        servidor.start()
        cliente_socket, addr = servidor.conexao.accept()
        
        # msg = cliente_socket.recv(1000).decode('utf-8')



    elif tipo == 1:
        nome = input("Nome do usuário: ")
        cliente = Cliente(nome)
        cliente.start(endereco, porta)

        # Le metadados do arquivo
        nome_arq = input("Nome do arquivo: ")
        tam_pac = float(input("Tamanho do pacote: "))
        file = open(nome_arq)
        qtd_pac = math.ceil((os.path.getsize(nome_arq))/tam_pac)
        
        # envia metadados    
        json = {"nome":os.path.basename(nome_arq),"tam_pac":tam_pac,"qtd_pac":qtd_pac}
        cliente.conexao.send((Pacote.encode(0,json)))


        for i in range(1,qtd_pac+1):
            dado = file.read(tam_pac)
            cliente.conexao.send((Pacote.encode(i,dado)))
    
