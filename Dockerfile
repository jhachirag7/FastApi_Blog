FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /fastapi_blog
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
COPY . .