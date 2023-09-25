FROM python:3.10

WORKDIR /usr/src/app

RUN mkdir /usr/src/app/media
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY /Megano/ /usr/src/app/

EXPOSE 8000
RUN python manage.py migrate
RUN python manage.py loaddata catalog_dump
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
