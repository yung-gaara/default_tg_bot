FROM python:3.10-buster

RUN apt-get update && \
    apt-get install -y \
        libpq-dev \
        curl \
        openssl \
        nano && \
    rm -rf /var/lib/apt/lists/*

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

ADD ./src/tg_bot/requirements.txt /source/requirements.txt
RUN pip install -r /source/requirements.txt

ENV PYTHONIOENCODING utf8

COPY ./bin/tg_bot/start_bot.py /source/run.py
COPY ./src/tg_bot /source/tg_bot

WORKDIR /source/

CMD ["python3.10", "run.py"]
