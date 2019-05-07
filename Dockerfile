FROM python:3.6.7

MAINTAINER "sidh711@gmail.com"

ENV PYTHONUNBUFFERED 1

RUN useradd -u 1000 siddhesh -d /home/siddhesh

RUN mkdir -p /home/siddhesh/bin
RUN chown -R siddhesh:siddhesh /home/siddhesh

ENV PATH="/home/siddhesh/bin:${PATH}"

USER siddhesh

RUN mkdir -p /home/siddhesh/parkinglot

RUN cd /home/siddhesh/

RUN python3 -m venv /home/siddhesh/parkinglot_env \
    && ls -al

WORKDIR /home/siddhesh/parkinglot

RUN /bin/bash -c "source /home/siddhesh/parkinglot_env/bin/activate \
    && pip install --upgrade pip \
    && pwd && ls"

COPY ./requirements*.txt /home/siddhesh/parkinglot/

RUN /bin/bash -c "source /home/siddhesh/parkinglot_env/bin/activate \
    && pip install -r requirements.txt"

USER root
RUN rm -rf /home/siddhesh/parkinglot

RUN ln -s /home/siddhesh/parkinglot_env/bin/python /home/siddhesh/bin/parkinglot_env \
    && chmod 755 /home/siddhesh/bin/parkinglot_env