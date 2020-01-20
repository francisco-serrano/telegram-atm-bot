FROM python:3.6.9 as base

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt
RUN apt update
RUN apt install -y cron
RUN apt install nano

FROM base as dev

WORKDIR /app

ADD . /app

ENV DB_DIR /app/database/cajeros.db
ENV CSV_DIR /app/data/cajeros-automaticos.csv
ENV TABLE_NAME cajeros
ENV TELEGRAM_TOKEN 922536530:AAHVi0P3rVipLMDpln7NSl71VMCbOgYBS8E

RUN printf "0 8 * * 1-5 root bash -l -c '/app/utils/scheduling/job.sh'\n# Empty line\n" >> /etc/cron.d/mycron
RUN chmod +x /etc/cron.d/mycron
RUN crontab /etc/cron.d/mycron
RUN chmod +x /app/utils/scheduling/job.sh