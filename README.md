# Python RabbitMQ Example

Este projeto demonstra a utilização do RabbitMQ para troca de mensagens entre um publicador (publisher) e um consumidor (worker) utilizando Python.

## Estrutura do Projeto

-   `publisher.py`: Um script Python que publica mensagens de exemplo (geradas com a biblioteca Faker) em uma fila do RabbitMQ.
-   `worker.py`: Um script Python que consome mensagens da mesma fila do RabbitMQ, processa-as e as reconhece (ack).
-   `.env.example`: Um arquivo de exemplo para as variáveis de ambiente necessárias.

## Pré-requisitos

Antes de começar, certifique-se de ter os seguintes softwares instalados:

-   **Python 3.x**: Recomendado Python 3.8 ou superior.
-   **pip**: Gerenciador de pacotes do Python (geralmente vem com o Python).
-   **Docker** e **Docker Compose**: Para executar o servidor RabbitMQ de forma isolada.

## Configuração do Ambiente

1.  **Clone o Repositório** (se ainda não o fez):
    ```bash
    git clone https://github.com/leonardosouza/python-rabbitmq.git
    cd python-rabbitmq
    ```

2.  **Crie o arquivo de variáveis de ambiente**:
    Crie um arquivo chamado `.env` na raiz do projeto (o mesmo diretório de `publisher.py` e `worker.py`) e preencha-o com as informações do seu servidor RabbitMQ. Você pode usar o `.env.example` como base:

    ```
    # .env.example
    RABBITMQ_HOST=localhost
    RABBITMQ_USER=guest
    RABBITMQ_PASS=guest
    RABBITMQ_QUEUE=my_queue
    ```

    Substitua `localhost`, `guest` e `my_queue` pelos valores apropriados se o seu RabbitMQ não estiver na configuração padrão.

3.  **Inicie o RabbitMQ com Docker Compose**:
    Você pode usar um `docker-compose.yml` para iniciar o RabbitMQ de forma simples. Crie um arquivo `docker-compose.yml` na raiz do seu projeto com o seguinte conteúdo:

    ```yaml
    version: '3.8'
    services:
      rabbitmq:
        image: rabbitmq:3-management-alpine
        hostname: rabbitmq
        ports:
          - "5672:5672"
          - "15672:15672" # Porta para a interface de gerenciamento
        environment:
          RABBITMQ_DEFAULT_USER: guest
          RABBITMQ_DEFAULT_PASS: guest
        volumes:
          - rabbitmq_data:/var/lib/rabbitmq
    
    volumes:
      rabbitmq_data:
    ```

    Após criar o arquivo, inicie o serviço Docker:

    ```bash
    docker-compose up -d
    ```
    Isso iniciará um contêiner RabbitMQ e o tornará acessível em `localhost:5672` (e a interface de gerenciamento em `localhost:15672`).

## Instalação de Dependências

Instale as bibliotecas Python necessárias usando `pip`:

```bash
pip install pika python-dotenv Faker
```

## Como Executar

Certifique-se de que o RabbitMQ esteja em execução (conforme o passo 3 em "Configuração do Ambiente").

1.  **Inicie o Worker (Consumidor)**:
    Abra um terminal e execute o script `worker.py`. Este script ficará aguardando por mensagens na fila.

    ```bash
    python worker.py
    ```

2.  **Inicie o Publisher (Publicador)**:
    Abra **outro** terminal e execute o script `publisher.py`. Este script publicará mensagens na fila do RabbitMQ.

    ```bash
    python publisher.py
    ```

    Você verá o `publisher.py` enviando mensagens e o `worker.py` recebendo e processando-as.

## Detalhes Técnicos

-   **`worker.py`**: Implementa uma lógica de reconexão automática ao RabbitMQ em caso de perda de conexão. Utiliza `basic_qos(prefetch_count=1)` para garantir que o worker processe apenas uma mensagem por vez e `basic_nack(requeue=False)` para mensagens que falham no processamento, evitando loops infinitos.
-   **`publisher.py`**: Gera 100.000 mensagens com dados falsos usando a biblioteca `Faker` e as publica na fila com `delivery_mode=2` para torná-las persistentes (sobrevivem a reinícios do broker).
-   **Variáveis de Ambiente**: As credenciais e o nome da fila do RabbitMQ são carregados de um arquivo `.env` para maior segurança e flexibilidade.

---
Espero que isso ajude! Se tiver mais alguma dúvida, é só perguntar. 