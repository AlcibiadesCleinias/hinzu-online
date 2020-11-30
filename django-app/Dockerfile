# pull official base image
# FROM python:3.8.0-alpine
FROM python:3.6

# set work directory
WORKDIR /usr/src/app

# set environment variables
# no writing pyc files
# prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
#RUN apk update \
#    && apk add postgresql-dev gcc python3-dev musl-dev
RUN apt-get update \
     && apt-get -y install gcc libpq-dev python3-dev netcat

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --default-timeout=2000 -r requirements.txt
RUN pip install hnswlib==0.3.4

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
