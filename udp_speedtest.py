import logging
from datetime import datetime, timedelta
from socket import timeout
from speedtest import Resultado, TesteRede, TipoSocket, FuncaoCliente

class RedesUDPSpeed(TesteRede):
    """
    Classe modificada para realizar a transmissão de dados via UDP e calcular
    as velocidades de download e upload entre máquinas.
    """

    PACOTE_CONFIRMACAO = b"\x01"

    def __init__(self, local_endereco: str, remoto_endereco: str, porta: int, funcao_inicial: FuncaoCliente):
        super().__init__(local_endereco, remoto_endereco, porta, funcao_inicial, TipoSocket.UDP)

    def receber_pacotes(self) -> Resultado:
        """
        Recebe os pacotes enviados, contando os bytes recebidos.
        """
        self.connection.settimeout(1)
        bytes_recebidos = 0
        aguardando_mensagem = False
        proximo_tempo = datetime.now() + timedelta(seconds=1)

        while True:
            try:
                pacote = self.recvall(self.connection, self.TAMANHO_PACOTE)
                if pacote == self.EMPTY_PACKET:
                    break

                if bytes_recebidos == 0 and not aguardando_mensagem:
                    print("Iniciando teste de download...")

                logging.debug("Recebido %d bytes, total até agora: %d", len(pacote), bytes_recebidos)

                bytes_recebidos += len(pacote)

                if datetime.now() >= proximo_tempo:
                    proximo_tempo = datetime.now() + timedelta(seconds=1)
            except timeout:
                self.connection.send(self.EMPTY_PACKET)
            except ConnectionRefusedError:
                if not aguardando_mensagem:
                    print("Aguardando conexão do remetente...")
                    aguardando_mensagem = True

        logging.debug("Recepção de pacotes finalizada.")

        pacote_estatisticas = self.encode_stats_packet(bytes_recebidos)
        self.connection.send(pacote_estatisticas)

        while True:
            try:
                bytes_enviados = self.connection.recv(self.TAMANHO_INTEIRO_BYTES)
                bytes_enviados = self.decode_stats_packet(bytes_enviados)
                confirmacao = self.connection.recv(self.TAMANHO_PACOTE)
                if confirmacao == self.PACOTE_CONFIRMACAO:
                    break
            except timeout:
                continue

        return Resultado(bytes_enviados, bytes_recebidos)

    def enviar_pacotes(self) -> Resultado:
        """
        Função que realiza o envio de pacotes UDP e, ao final, confirma os bytes recebidos.
        """
        print("Aguardando conexão do destinatário...")
        _, endereco = self.connection.recvfrom(self.TAMANHO_PACOTE)
        print("Iniciando o teste de upload...")

        tempo_fim = datetime.now() + timedelta(seconds=self.DURACAO_TESTE)
        total_bytes_transmitidos = 0

        logging.debug("Iniciando envio de pacotes")
        while datetime.now() < tempo_fim:
            self.connection.sendto(self.dados, endereco)
            total_bytes_transmitidos += len(self.dados)

        logging.debug("Envio de pacotes finalizado.")
        self.connection.settimeout(1)

        bytes_recebidos = 0
        while bytes_recebidos == 0:
            try:
                self.connection.sendto(self.EMPTY_PACKET, endereco)
                pacote_recebido = self.connection.recv(self.TAMANHO_INTEIRO_BYTES)
                bytes_recebidos = self.decode_stats_packet(pacote_recebido)

                pacote_estatisticas = self.encode_stats_packet(total_bytes_transmitidos)
                self.connection.sendto(pacote_estatisticas, endereco)

                self.connection.sendto(self.PACOTE_CONFIRMACAO, endereco)
            except timeout:
                continue

        logging.debug("Número total de bytes confirmados: %d", bytes_recebidos)

        return Resultado(total_bytes_transmitidos, bytes_recebidos)
