FROM python:3.10.4-alpine3.15

RUN mkdir /app
WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt

ENV FLASK_APP app.py
ENV FLASK_DEBUG 1

CMD ["flask", "run", "-h", "0.0.0.0"]