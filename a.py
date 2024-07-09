import socket

def start_client(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    while True:
        message = input("Você: ")
        client.send(message.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        print(f"Servidor: {response}")

if __name__ == "__main__":
    ip = input("Digite o endereço IP do servidor: ")
    port = int(input("Digite a porta TCP do servidor: "))
    start_client(ip, port)