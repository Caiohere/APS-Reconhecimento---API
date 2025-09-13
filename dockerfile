# Usar uma imagem oficial do Python como base
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instalar as dependências do sistema operacional
RUN apt-get update && apt-get install -y build-essential cmake

# --- ADICIONE ESTA LINHA ---
# Força a compilação a usar apenas um núcleo para economizar RAM
ENV MAX_JOBS=1

# Copiar o arquivo de requisitos
COPY requirements.txt requirements.txt

# Instalar as bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o resto do código do seu projeto
COPY . .

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]