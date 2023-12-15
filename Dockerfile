FROM  python:alpine3.19
WORKDIR /app



# copy requirements and install (so that changes to files do not mean rebuild cannot be cached)
COPY ./ .

RUN pip3 install -r requirements.txt


# run supervisord
CMD ["./supervisord"]