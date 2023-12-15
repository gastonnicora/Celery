FROM  python:3.8.16-alpine3.18
WORKDIR /app



# copy requirements and install (so that changes to files do not mean rebuild cannot be cached)
COPY ./ .

RUN pip3 install -r requirements.txt

# expose port 80 of the container (HTTP port, change to 443 for HTTPS)
EXPOSE 80

# needs to be set else Celery gives an error (because docker runs commands inside container as root)
ENV C_FORCE_ROOT=1

# run supervisord
CMD ["./supervisord"]