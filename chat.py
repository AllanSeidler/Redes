import socket

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


if __name__ == "__main__":
    endereco = input("Endereço do servidor: ")
    porta = int(input("Porta do servidor: "))
    tipo = int(input("Cliente(1) ou Servidor(2): "))

    if tipo==2:
        servidor = Servidor(endereco, porta)
        servidor.start()
        cliente_socket, addr = servidor.conexao.accept()
        
        while True:
            msg = cliente_socket.recv(1024).decode('utf-8')
            print(f"Usuario: {msg}")
            msg = input("Voce: ")
            cliente_socket.send(("Servidor: "+msg).encode('utf-8'))
            if not msg:
                break
        cliente_socket.close()

    elif tipo == 1:
        nome = input("Nome do usuário: ")
        cliente = Cliente(nome)
        cliente.start(endereco, porta)

        while True:
            msg = input("Voce: ")
            cliente.conexao.send((nome+": "+msg).encode('utf-8'))
            msg = cliente.conexao.recv(1024).decode('utf-8')
            print(f"Servidor: {msg}")
            if not msg:
                break
        cliente.conexao.close()
