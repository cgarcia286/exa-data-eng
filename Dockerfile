FROM python:3.11.5-alpine3.18

RUN pip install --upgrade pip

WORKDIR /app

COPY /requirements /app/requirements
COPY /data /app/data

RUN pip install --no-cache-dir -r requirements/local.txt

COPY /src /app/src

COPY crontab /app

RUN crontab /app/crontab

CMD ["crond", "-f"]
