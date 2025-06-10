from dotenv import load_dotenv
import os
import time
import json
import logging

import pika
from pika.exceptions import AMQPConnectionError, StreamLostError

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def connect_rabbitmq():
    """
    Tenta conectar ao RabbitMQ repetidamente até ter sucesso.
    Retorna a tupla (connection, channel).
    """
    host       = os.getenv("RABBITMQ_HOST")
    user       = os.getenv("RABBITMQ_USER")
    password   = os.getenv("RABBITMQ_PASS")
    queue_name = os.getenv("RABBITMQ_QUEUE")

    if not all([host, user, password, queue_name]):
        logging.error("Uma ou mais variáveis de ambiente do RabbitMQ não estão definidas.")
        logging.error("Por favor, defina RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASS e RABBITMQ_QUEUE.")
        raise ValueError("Variáveis de ambiente do RabbitMQ ausentes")

    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(
        host=host,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30
    )

    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            # Declara fila durable (sobrevive a restart do broker)
            channel.queue_declare(queue=queue_name, durable=True)
            # Garantir que só receba 1 mensagem por vez
            channel.basic_qos(prefetch_count=1)

            logging.info(f"Conectado ao RabbitMQ em {host}, fila='{queue_name}'")
            return connection, channel

        except AMQPConnectionError as e:
            logging.error(f"Falha na conexão: {e}. Tentando novamente em 5s...")
            time.sleep(5)

def process_message(body):
    """
    Aqui você coloca a lógica de processamento da mensagem.
    """
    data = json.loads(body)
    # Exemplo de processamento:
    logging.info(f"Processando payload: {data}")
    # ... faça algo com data ...

def on_message(ch, method, properties, body):
    """
    Callback executado para cada mensagem recebida.
    """
    try:
        on_message_delivery_tag = method.delivery_tag
        logging.info(f"Mensagem recebida (delivery_tag={on_message_delivery_tag})")
        
        process_message(body)

        # Acknowledge: informa ao RabbitMQ que processou com sucesso
        ch.basic_ack(delivery_tag=on_message_delivery_tag)
        logging.info(f"Mensagem acked (delivery_tag={on_message_delivery_tag})")

    except Exception as e:
        logging.exception(f"Erro ao processar mensagem: {e}")
        # Nack sem requeue para evitar loop infinito em mensagens malformadas
        ch.basic_nack(delivery_tag=on_message_delivery_tag, requeue=False)

if __name__ == "__main__":
    # Não é mais necessário obter a variável de ambiente aqui,
    # pois connect_rabbitmq() já a obtém.
    # queue_name = os.getenv("RABBITMQ_QUEUE") 

    while True:
        connection, channel = connect_rabbitmq()
        try:
            # Usar a fila declarada na conexão
            channel.basic_consume(
                queue=os.getenv("RABBITMQ_QUEUE"), # Obtém novamente para basic_consume
                on_message_callback=on_message
            )
            logging.info("Iniciando o consumo de mensagens...")
            channel.start_consuming()

        except StreamLostError:
            logging.warning("Conexão perdida. Reconectando...")
            # Loop vai reiniciar a conexão

        except KeyboardInterrupt:
            logging.info("Interrompido pelo usuário. Fechando conexão...")
            channel.stop_consuming()
            connection.close()
            break
