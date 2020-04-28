FROM python:3

WORKDIR /usr/src/app
RUN mkdir tmp -p && mkdir volumes -p

COPY requirements.txt ./
RUN apt-get update -qq && apt-get -y install \
	ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py server.py
COPY shazam.py shazam.py

CMD [ "python", "./server.py" ]
