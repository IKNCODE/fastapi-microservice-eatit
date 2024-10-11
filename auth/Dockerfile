FROM python:3.12

COPY requirements.txt requiremenets.txt
RUN pip install -r requiremenets.txt

COPY . .
EXPOSE 8000
WORKDIR .
ENV DB_HOST=host.docker.internal
ENV DB_PORT=5432
ENV DB_NAME=eatit_auth
ENV DB_USER=postgres
ENV DB_PASS=123

CMD ["uvicorn" , "main:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "/aut"]