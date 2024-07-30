import socket
import json
import os
import math
import hashlib

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
    separador = 'separador™'
    separador_pk = 'separador☺'
    hash2 = hashlib.sha256()

    @staticmethod
    def encode(id,payload):
        header = f"{id}"
        packet = f"{header}{Pacote.separador}{payload}"
        Pacote.hash2.update(packet.encode('utf-8'))
        checksum = Pacote.hash2.hexdigest()
        packet = f"{packet}{Pacote.separador}{checksum}"#{Pacote.separador_pk}"
        binary_packet = packet.encode()
        return binary_packet
    
    @staticmethod
    def decode(binary_packet):
        packet = binary_packet.decode('utf-8')
        #packets = packet.split(Pacote.separador_pk)
        return packet.split(Pacote.separador)
    

    @staticmethod
    def check(packet):
        try:
            id,payload,checksum = packet
        except:
            return False
        header = f"{id}"
        p = f"{header}{Pacote.separador}{payload}"
        Pacote.hash2.update(p.encode('utf-8'))
        checksum = Pacote.hash2.hexdigest()
        return checksum==Pacote.hash2.hexdigest()


if __name__ == "__main__":
    endereco = input("Endereço do servidor: ")
    porta = int(input("Porta do servidor: "))
    tipo = int(input("Cliente(1) ou Servidor(2): "))
    
    if tipo==2:
        # abre o servidor
        servidor = Servidor(endereco, porta)
        servidor.start()
        cliente_socket, addr = servidor.conexao.accept()
        
        
        # recebe os meta dados
        md = Pacote.decode(cliente_socket.recv(1000))
        if(Pacote.check(md)):
            metadados = json.loads(str.replace(md[1],'\'','\"'))
            nome = metadados['nome']
            tam_pac=metadados['tam_pac']
            qtd_pac=metadados['qtd_pac']

            buffer=[]
            for i in range(1,qtd_pac+1):
                buffer.append(Pacote.decode(cliente_socket.recv(tam_pac+500)))

            # buffer.sort();
            file = open(nome,"w")
            for i in range(0,qtd_pac):
                
                if(Pacote.check(buffer[i])):
                    print("ok ",end="")
                    file.write(buffer[i][1])
                else:
                    print("erro na transferencia")
                    file.close()
                    break


        else:
            print("erro na transferencia!")
            
    elif tipo == 1:
        nome = ""#input("Nome do usuário: ")
        cliente = Cliente(nome)
        cliente.start(endereco, porta)

        tam_pacs = [500,1000,1500]

        # Le metadados do arquivo
        nome_arq = input("Nome do arquivo: ")
        tam_pac = tam_pacs[int(input("Tamanho do pacote\n[1] - 500\n[2] - 1000\n[3] - 1500\n"))-1]
        file = open(nome_arq)
        qtd_pac = math.ceil((os.path.getsize(nome_arq))/float(tam_pac))
        
        # envia metadados    
        md = {"nome":os.path.basename(nome_arq),"tam_pac":tam_pac,"qtd_pac":qtd_pac}
        cliente.conexao.send((Pacote.encode(0,md)))


        for i in range(1,qtd_pac+1):
            dado = file.read(tam_pac+300)
            cliente.conexao.send((Pacote.encode(i,dado)))
    
