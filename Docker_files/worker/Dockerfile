# syntax=docker/dockerfile:1

FROM python:3.10.2

WORKDIR /worker

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY pystributor/ .

EXPOSE 6337:6337

CMD ["python3", "pystributor_worker.py"]