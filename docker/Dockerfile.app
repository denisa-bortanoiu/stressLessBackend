FROM python:alpine3.7
RUN apk update && apk add --virtual build-dependencies build-base gcc wget git
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install numpy
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
EXPOSE 5000
