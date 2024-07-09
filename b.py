import socket
import threading

#127.0.0.1 5000

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Cliente: {message}")
            response = input("Você: ")
            client_socket.send(response.encode('utf-8'))
        except:
            break
    client_socket.close()

def start_server(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)
    print(f"Servidor ouvindo em {ip}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexão aceita de {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    ip = input("Digite o endereço IP do servidor: ")
    port = int(input("Digite a porta TCP do servidor: "))
    start_server(ip, port)