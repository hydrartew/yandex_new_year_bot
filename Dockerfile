FROM python:3.12

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

WORKDIR /app

COPY . .

CMD ["sh", "-c", "ls -R /app && python main.py"]