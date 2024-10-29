FROM python:3.12

COPY requirements.txt requiremenets.txt
RUN pip install psycopg2 \
    && pip install -r requiremenets.txt

COPY . .
EXPOSE 8001
WORKDIR .
ENV DB_HOST=host.docker.internal
ENV DB_PORT=5432
ENV DB_NAME=eatit_store
ENV DB_USER=postgres
ENV DB_PASS=123
CMD ["uvicorn" , "main:app", "--host", "0.0.0.0", "--port", "8001", "--root-path", "/api"]