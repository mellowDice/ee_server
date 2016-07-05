FROM python:3.5.1-onbuild

RUN mkdir app
ADD . /app
WORKDIR /app

RUN export APP_CONFIG_FILE='./config/production.py'


COPY requirements.txt /app

EXPOSE 9000

ENTRYPOINT ["python", "main.py"]