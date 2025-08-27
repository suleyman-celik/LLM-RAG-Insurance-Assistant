FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY Data/data.csv Data/data.csv
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY assistant .
# RUN apt-get update && apt-get install -y tzdata \
#     && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
#     && echo $TZ > /etc/timezone

EXPOSE 5001

CMD gunicorn --bind 0.0.0.0:5001 app:app