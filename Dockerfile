FROM python:3.12

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

WORKDIR /app

COPY . .

ARG PATH_REDIS_CRT=/app/configs/.redis

RUN apt-get update && \
    mkdir -p ${PATH_REDIS_CRT} && \
    wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
         --output-document ${PATH_REDIS_CRT}/YandexInternalRootCA.crt && \
    chmod 0655 ${PATH_REDIS_CRT}/YandexInternalRootCA.crt

CMD ["sh", "-c", "ls -R /app && python main.py"]