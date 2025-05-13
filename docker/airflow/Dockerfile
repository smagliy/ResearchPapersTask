FROM apache/airflow:2.5.0-python3.10

USER root
RUN apt update && \
    apt-get install -y zip && \
    apt-get clean;

USER airflow
RUN python3 -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src src
RUN chmod 777 ./




