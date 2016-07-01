FROM tiangolo/uwsgi-nginx-flask:flask

RUN mkdir app
ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt 

EXPOSE 7000

ENTRYPOINT ["python", "main.py"]