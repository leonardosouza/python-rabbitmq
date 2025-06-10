# ---- etapa de build ----
FROM python:3.11-alpine AS builder

# Instala dependências de compilação (se precisar de alguma lib nativa)
RUN apk add --no-cache build-base

WORKDIR /app

# Copia o requirements e instala pacotes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- etapa final ----
FROM python:3.11-alpine

# Copia só o que precisamos do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

WORKDIR /app

# Copia o código da aplicação
COPY . .

# Define variável de ambiente para conexão
ENV PYTHONUNBUFFERED=1

# Comando padrão
CMD ["python", "worker.py"]
