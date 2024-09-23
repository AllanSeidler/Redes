import sys
from speedtest import FuncaoCliente
from udp_speedtest import RedesUDPSpeed
from tcp_speedtest import RedesTCPSpeed

def executar_teste():
    """ Entrada dos dados de endereço, porta e operação. """
    endereco_local = input("Endereço local: ")
    endereco_remoto = input("Endereço remoto: ")
    porta = int(input("Número da porta: "))
    tipo_cliente = input("[E] Enviar || [R] Receber: ")

    if porta < 1000 or porta > 65535:
        print("Porta deve estar entre 1000 e 65535.")
        sys.exit(1)

    if tipo_cliente.lower() == "e":
        funcao_inicial = FuncaoCliente.REMETENTE
    elif tipo_cliente.lower() == "r":
        funcao_inicial = FuncaoCliente.DESTINATARIO
    else:
        print("Opção inválida.")
        sys.exit(1)

    teste_tcp = RedesTCPSpeed(endereco_local, endereco_remoto, porta, funcao_inicial)
    teste_tcp.iniciar()
    teste_udp = RedesUDPSpeed(endereco_local, endereco_remoto, porta, funcao_inicial)
    teste_udp.iniciar()

if __name__ == "__main__":
    executar_teste()
