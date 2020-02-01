FROM python:3-alpine

WORKDIR /app

RUN apk add --no-cache ffmpeg && \
  wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl && \
  chmod a+rx /usr/local/bin/youtube-dl

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./api.py" ]

EXPOSE 9029
VOLUME /config /download
