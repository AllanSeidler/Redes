import logging
import socket
from abc import ABCMeta, abstractmethod
from enum import Enum
from random import randbytes
from time import sleep
from typing import Dict

class TipoSocket(Enum):
    TCP = socket.SOCK_STREAM
    UDP = socket.SOCK_DGRAM

class FuncaoCliente(Enum):
    REMETENTE = "upload"
    DESTINATARIO = "download"

class Resultado: 
    """ Armazena os resultados de um teste de rede. """

    def __init__(self, bytes_transmitidos: int, bytes_recebidos: int) -> None:
        self.bytes_transmitidos = bytes_transmitidos
        self.bytes_recebidos = bytes_recebidos

    @staticmethod
    def formatar_bytes(tamanho) -> str:
        """ Formata o valor passado para Gb, Mb, Kb etc"""
        index = 0
        valores = {0: "b", 1: "Kb", 2: "Mb", 3: "Gb", 4: "Tb"}
        while tamanho > 1024 and index < 4:
            tamanho /= 1024
            index += 1
        return f"{round(tamanho, 2)} {valores[index]}"

    def relatorio(self, tamanho_pacote: int, duracao_teste: int, funcao: FuncaoCliente) -> None:
        """ Imprime um relatorio dos resultados obtidos. """
        pacotes_enviados = (self.bytes_transmitidos)/tamanho_pacote
        pacotes_perdidos = (self.bytes_transmitidos - self.bytes_recebidos)/tamanho_pacote
        pacotes_por_segundo = int(self.bytes_recebidos / (duracao_teste * tamanho_pacote))
        taxa_bits_por_segundo = (self.bytes_recebidos * 8) / duracao_teste
        velocidade_formatada = self.formatar_bytes(taxa_bits_por_segundo)

        print(f"{str(funcao.value).capitalize()}")
        print(f"Tamanho dos pacotes: {tamanho_pacote} bytes")
        print(f"Tempo de execução do teste: {duracao_teste}s")
        print(f"Total de bytes transmitidos: {self.bytes_transmitidos:,} bytes. Ou ainda {self.formatar_bytes(self.bytes_transmitidos)}")
        print(f"Pacotes enviados: {pacotes_enviados:,.0f}")
        print(f"Pacotes perdidos: {pacotes_perdidos:,.0f}")
        print(f"Pacotes por segundo: {pacotes_por_segundo:,} p/s")
        print(f"Velocidade de {funcao.value}: {velocidade_formatada}/s")

class TesteRede(metaclass=ABCMeta):
    DURACAO_TESTE = 20
    TAMANHO_INTEIRO_BYTES = 8
    TAMANHO_PACOTE = 500
    EMPTY_PACKET = b"\x00" * TAMANHO_PACOTE

    def __init__(self, endereco_escuta: str, endereco_conectar: str, porta: int, funcao_inicial: FuncaoCliente, tipo_socket: TipoSocket):
        self.connection = socket.socket(socket.AF_INET, tipo_socket.value)
        self.listen_address = (endereco_escuta, porta)
        self.connect_address = (endereco_conectar, porta)
        self.tipo_socket = tipo_socket
        self.funcao = funcao_inicial
        self.dados = b'teste de rede *2024*:Objetivo: ferramenta para testar a velocidade de conexao de rede entre dois computadores. Utilizar preferencialmente a linguagem Phyton. Cada Equipe devera cumprir os seguintes objetivos, listados abaixo: Avaliar a taxa de transferencia para download e upload entre dois computadores de forma separada para os protocolos TCP e UDP. Executar o programa, na rede cabeada e sem fio e responder as questoes a seguir: Quantos pacotes foram enviados? E quantos foram perdidos? allanESM' #randbytes(self.TAMANHO_PACOTE)

    def __del__(self):
        self.connection.close()

    def executar_funcao(self) -> Resultado:
        logging.debug("Executando função: %s", self.funcao.name)
        if self.funcao == FuncaoCliente.DESTINATARIO:
            sleep(2)
            self.connection.connect(self.connect_address)
            resultado = self.receber_pacotes()
            return resultado
        if self.funcao == FuncaoCliente.REMETENTE:
            sleep(1)
            self.connection.bind(self.listen_address)
            resultado = self.enviar_pacotes()
            return resultado
        return Resultado(0, 0)

    def iniciar(self) -> None:
        print(f"Iniciando teste com socket {self.tipo_socket.name}...")
        dados_relatorio = {
            FuncaoCliente.DESTINATARIO: None,
            FuncaoCliente.REMETENTE: None,
        }
        dados_relatorio[self.funcao] = self.executar_funcao()
        self.alternar_funcao()
        dados_relatorio[self.funcao] = self.executar_funcao()
        self.exibir_relatorio(dados_relatorio)

    def exibir_relatorio(self, resultados: Dict[FuncaoCliente, Resultado]) -> None:
        print("-----------------------------------------------------------")
        print(f"Resultados usando socket {self.tipo_socket.name}\n")
        for funcao, resultado in resultados.items():
            resultado.relatorio(self.TAMANHO_PACOTE, self.DURACAO_TESTE, funcao)
            print()
        print("-----------------------------------------------------------")

    def alternar_funcao(self) -> None:
        logging.debug("Alterando função")
        if self.funcao == FuncaoCliente.DESTINATARIO:
            self.funcao = FuncaoCliente.REMETENTE
        elif self.funcao == FuncaoCliente.REMETENTE:
            self.funcao = FuncaoCliente.DESTINATARIO
        self.connection.close()
        self.connection = socket.socket(socket.AF_INET, self.tipo_socket.value)

    @staticmethod
    def recvall(sock, tamanho):
        dados = b""
        while len(dados) < tamanho:
            buffer = sock.recv(tamanho - len(dados))
            dados += buffer
        return dados
    
    def encode_stats_packet(self, value: int) -> bytes:
        """
        Cria um pacote de estatísticas, contendo bytes transmitidos e o número de pacotes
        perdidos.
        """
        return value.to_bytes(self.TAMANHO_INTEIRO_BYTES, "big", signed=False)

    def decode_stats_packet(self, stats_packet: bytes) -> int:
        """
        Decodifica um pacote de estatísticas, contendo bytes transmitidos e o número de pacotes
        perdidos.
        """
        return int.from_bytes(stats_packet, "big", signed=False)

    @abstractmethod
    def receber_pacotes(self) -> Resultado:
        raise NotImplementedError("Método receber_pacotes() precisa ser implementado.")

    @abstractmethod
    def enviar_pacotes(self) -> Resultado:
        raise NotImplementedError("Método enviar_pacotes() precisa ser implementado.")
