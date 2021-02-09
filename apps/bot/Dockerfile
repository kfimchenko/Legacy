FROM python:3.9

RUN apt-get update && apt-get install -y poppler-utils

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./__main__.py" ]