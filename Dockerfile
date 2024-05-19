FROM  python:alpine3.19
WORKDIR /usr/src/app

# install supervisord
RUN apk update && apk add --no-cache supervisor

# copy requirements and install (so that changes to files do not mean rebuild cannot be cached)
COPY requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# copy all files into the container
COPY . /usr/src/app

# expose port 80 of the container (HTTP port, change to 443 for HTTPS)
EXPOSE 80

# needs to be set else Celery gives an error (because docker runs commands inside container as root)
ENV C_FORCE_ROOT=1
ENV REDIS=redis

# run supervisord
CMD ["/usr/bin/supervisord"]