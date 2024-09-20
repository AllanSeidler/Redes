import logging
import sys

from speedtest import Roles
from speedtest_udp import SpeedTestUDP
from speedtest_tcp import SpeedTestTCP


"""
Lê os argumentos fornecidos pelo usuário, cria e executa as funções de envio e recebimento.
"""

listen_address = input("Seu endereço: ")
connect_address = input("Endereço do outro usuário: ")
port = int(input("Porta: "))
client_type = input("Enviar[E] ou receber[R]?: ")

if port < 4999 or port > 6000:
    print("Porta deve ser 5000 alguma coisa!")
    sys.exit(1)

if client_type.lower() == "e":
    starting_role = Roles.SENDER
elif client_type.lower() == "r":
    starting_role = Roles.RECEIVER
else:
    print("Opção inválida!")
    sys.exit(1)


# tcp_tester = SpeedTestTCP(listen_address, connect_address, port, starting_role)
# tcp_tester.run()
udp_tester = SpeedTestUDP(listen_address, connect_address, port, starting_role)
udp_tester.run()

