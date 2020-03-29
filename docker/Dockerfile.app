FROM python:alpine3.7
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
EXPOSE 5000
