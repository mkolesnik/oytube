FROM python:3-alpine

WORKDIR /app

RUN apk add --no-cache ffmpeg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV BUSTUBE_DOWNLOAD_DIR="/download" BUSTUBE_CONFIG_DIR="/config"

COPY . .

CMD [ "python", "-u", "./api.py" ]

EXPOSE 9029
VOLUME /config /download
