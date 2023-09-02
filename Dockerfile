FROM python:3.10-alpine
MAINTAINER Maksim Tiupa

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /kan
WORKDIR /kan
COPY . /kan

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN apk add --update bash && rm -rf /var/cache/apk/*
RUN pip install --upgrade pip
RUN pip install -r /kan/requirements.txt
RUN apk del .tmp-build-deps

RUN adduser -D user
USER user