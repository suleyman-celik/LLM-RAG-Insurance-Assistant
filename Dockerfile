FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY Data/data.csv Data/data.csv
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY customer_assist .
# RUN apt-get update && apt-get install -y tzdata \
#     && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
#     && echo $TZ > /etc/timezone

EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:5000 app:app