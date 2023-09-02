FROM python:3.11.5-slim-bullseye

RUN pip install --upgrade pip

WORKDIR /app

COPY /requirements /app/requirements
COPY /data /app/data

RUN pip install --no-cache-dir -r requirements/local.txt

COPY /src /app/src

CMD [ "python", "src/main.py" ]
