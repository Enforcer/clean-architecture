import sys

from main import bootstrap_app
from rq import Connection, Worker

app = bootstrap_app()

with Connection():
    queues = sys.argv[1:] or ["default"]
    w = Worker(queues)
    w.work()
