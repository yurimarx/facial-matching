FROM python:3.9-slim

WORKDIR /app

# Atualiza e instala as dependências modernas de interface gráfica (necessárias para OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instala as bibliotecas Python
RUN pip3 install --no-cache-dir streamlit requests pandas

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "appface.py", "--server.port=8501", "--server.address=0.0.0.0"]