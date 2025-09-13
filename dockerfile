FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential cmake

ENV MAX_JOBS=1

COPY requirements.txt requirements.txt

# --- ADICIONE ESTAS LINHAS PARA CRIAR O SWAP ---
# Aloca um arquivo de 2GB para ser usado como memória virtual
RUN fallocate -l 2G /swapfile
# Define as permissões corretas
RUN chmod 600 /swapfile
# Formata o arquivo como swap
RUN mkswap /swapfile
# Ativa o swap
RUN swapon /swapfile
# ---------------------------------------------------

# Agora, com o swap ativo, instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Desativa o swap depois de usar para limpar
RUN swapoff /swapfile

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]