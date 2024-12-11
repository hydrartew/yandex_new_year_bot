FROM python:3.12 AS compile-image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

FROM python:3.12
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY . .
CMD ["sh", "-c", "ls -R /app && python main.py"]