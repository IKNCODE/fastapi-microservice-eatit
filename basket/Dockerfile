FROM python:3.12

COPY requirements.txt requiremenets.txt
RUN pip install psycopg2 \
    && pip install -r requiremenets.txt

COPY . .
EXPOSE 8002
WORKDIR .
CMD ["python", "main.py"]