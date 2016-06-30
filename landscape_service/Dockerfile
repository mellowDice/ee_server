FROM python:3.5.1-onbuild

RUN mkdir app
ADD . /app
WORKDIR /app

COPY requirements.txt /app

EXPOSE 7000

ENTRYPOINT ["python", "main.py"]