FROM python:alpine

RUN apk add --no-cache --update exiftool
RUN pip install pyexiftool

ADD ./photo_sync.py /photo_sync.py

ENTRYPOINT ["python", "-u", "/photo_sync.py"]