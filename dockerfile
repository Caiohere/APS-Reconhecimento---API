FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential cmake

ENV MAX_JOBS=1

COPY requirements.txt requirements.txt

# --- ADICIONE ESTAS LINHAS PARA CRIAR O SWAP ---
RUN dd if=/dev/zero of=/swapfile bs=1M count=2048

# Define as permissões corretas
RUN chmod 600 /swapfile
# Formata o arquivo como swap
RUN mkswap /swapfile
# Ativa o swap
RUN swapon /swapfile
# ----------------------------------------------------------------

# Agora, com o swap ativo, instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Desativa e remove o swap depois de usar para limpar o ambiente final
RUN swapoff /swapfile
RUN rm /swapfile

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]