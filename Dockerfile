# for create the running for djanggo

FROM python:3.11.9-alpine

RUN pip install --upgrade pip


COPY ./requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /refactorbackend /app

COPY ./entrypoint.sh /
ENTRYPOINT [ "sh",'/entrypoint.sh' ]


