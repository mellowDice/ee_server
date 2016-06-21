FROM python:3.4-onbuild
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python manage.py