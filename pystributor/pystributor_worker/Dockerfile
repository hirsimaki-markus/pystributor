# syntax=docker/dockerfile:1

FROM python:3.10.2
WORKDIR /pystributor_worker

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 6116:6116

CMD ["python3", "pystributor_worker.py"]