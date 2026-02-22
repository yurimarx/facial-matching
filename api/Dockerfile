FROM serengil/deepface:latest

USER root

ENTRYPOINT []

WORKDIR /app

RUN pip install --no-cache-dir flask flask-cors intersystems-irispython

COPY download_models.py .
RUN python download_models.py

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "appface.py"]