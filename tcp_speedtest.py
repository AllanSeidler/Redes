import logging
from datetime import datetime, timedelta
from speedtest import Resultado, TesteRede, TipoSocket, FuncaoCliente

class RedesTCPSpeed(TesteRede):
    """
    Classe alterada para realizar a transmissão de dados via TCP e calcular
    as velocidades de download e upload entre máquinas.
    """

    def __init__(self, local_endereco: str, remoto_endereco: str, porta: int, funcao_inicial: FuncaoCliente):
        super().__init__(local_endereco, remoto_endereco, porta, funcao_inicial, TipoSocket.TCP)

    def receber_pacotes(self) -> Resultado:
        """
        Função que realiza a recepção de pacotes, contabilizando os bytes recebidos e,
        ao final, envia essa contagem ao remetente.
        """
        total_bytes_recebidos = 0
        proximo_tempo = datetime.now() + timedelta(seconds=1)

        while True:
            pacote = self.recvall(self.connection, self.TAMANHO_PACOTE)
            if pacote == self.EMPTY_PACKET:
                break

            logging.debug("Recebido %d bytes, total até agora: %d", len(pacote), total_bytes_recebidos)

            total_bytes_recebidos += len(pacote)

            # Controle do tempo
            if datetime.now() >= proximo_tempo:
                proximo_tempo = datetime.now() + timedelta(seconds=1)

        logging.debug("Recepção de dados finalizada.")

        pacote_estatisticas = self.encode_stats_packet(total_bytes_recebidos)
        self.connection.sendall(pacote_estatisticas)
        logging.debug("Número total de bytes recebidos enviado.")

        total_bytes_enviados = self.recvall(self.connection, self.TAMANHO_INTEIRO_BYTES)
        total_bytes_enviados = self.decode_stats_packet(total_bytes_enviados)
        logging.debug("Recepção finalizada.")

        return Resultado(total_bytes_enviados, total_bytes_recebidos)

    def enviar_pacotes(self) -> Resultado:
        """
        Função que realiza o envio de pacotes, contabilizando os bytes transmitidos.
        """
        print("Aguardando conexão do destinatário...")
        self.connection.listen()
        cliente, _ = self.connection.accept()
        print("Iniciando o envio de dados...")

        tempo_fim = datetime.now() + timedelta(seconds=self.DURACAO_TESTE)
        total_bytes_transmitidos = 0

        logging.debug("Iniciando envio de pacotes")
        while datetime.now() < tempo_fim:
            cliente.sendall(self.dados)
            total_bytes_transmitidos += len(self.dados)

        cliente.sendall(self.EMPTY_PACKET)
        logging.debug("Envio de pacotes finalizado.")

        total_bytes_recebidos = self.recvall(cliente, self.TAMANHO_INTEIRO_BYTES)
        total_bytes_recebidos = self.decode_stats_packet(total_bytes_recebidos)
        logging.debug("Número total de bytes recebidos pelo destinatário confirmado.")

        pacote_estatisticas = self.encode_stats_packet(total_bytes_transmitidos)
        cliente.sendall(pacote_estatisticas)

        logging.debug("Transmissão finalizada.")

        return Resultado(total_bytes_transmitidos, total_bytes_recebidos)
