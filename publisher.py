from dotenv import load_dotenv
import os
import json
import pika
from faker import Faker

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o Faker
fake = Faker()

# Parâmetros iguais aos do worker
host     = os.getenv("RABBITMQ_HOST")
user     = os.getenv("RABBITMQ_USER")
password = os.getenv("RABBITMQ_PASS")
queue    = os.getenv("RABBITMQ_QUEUE")

# Verifica se as variáveis de ambiente estão definidas
if not all([host, user, password, queue]):
    raise ValueError("Uma ou mais variáveis de ambiente do RabbitMQ não estão definidas no .env")

credentials = pika.PlainCredentials(user, password)
params = pika.ConnectionParameters(host=host, credentials=credentials)

# Conecta e declara a fila (durable=True para persistência)
conn    = pika.BlockingConnection(params)
channel = conn.channel()
channel.queue_declare(queue=queue, durable=True)

# Publica 1000 mensagens com payloads Faker
for i in range(1, 100001):
    message = {
        "id": i,
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address().replace("\n", ", "),
        "phone": fake.phone_number(),
        "company": fake.company(),
        "created_at": fake.iso8601()
    }
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)  # torna a mensagem persistente
    )
    print(f"✅ [{i:04d}/1000] Mensagem enviada: {message}")

conn.close()
