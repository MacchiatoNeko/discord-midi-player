FROM python:3.8-slim-buster

WORKDIR /

COPY . .

RUN apt-get update && apt-get install -y fluidsynth
RUN apt-get update && apt-get install -y ffmpeg

CMD ["sh", "start.sh"]
