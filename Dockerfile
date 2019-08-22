FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y wget
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

WORKDIR /usr/src/app
COPY auctions/requirements.txt auctions/requirements-dev.txt ./
RUN pip install pip-tools==3.8.0 -r requirements.txt -r requirements-dev.txt

COPY auctions/ ./
RUN make dev

ENV FLASK_APP='web_app/web_app/app.py:create_app()'
CMD ["flask", "run", "--host=0.0.0.0"]
ENTRYPOINT ["dockerize", "-wait", "tcp://database:5432"]

