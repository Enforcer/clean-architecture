FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y wget
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

WORKDIR /usr/src/app
COPY auctioning_platform/requirements.txt auctioning_platform/requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY auctioning_platform/ ./
RUN make dev

ENV FLASK_APP='web_app/web_app/app.py:create_app()'
CMD ["flask", "run", "--host=0.0.0.0"]
ENTRYPOINT ["dockerize", "-wait", "tcp://database:5432"]

