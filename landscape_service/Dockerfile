FROM docteurfraise/flask-python34

RUN mkdir app
ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 7000

CMD ["python", "main.py"]