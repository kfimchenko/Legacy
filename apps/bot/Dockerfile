FROM python:3.9-alpine3.12

RUN apk add poppler-utils

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./__main__.py" ]