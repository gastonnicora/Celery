import json
import os
from flask import Flask
from celery import Celery
import requests as R
from article import Articles
import redis
import threading
import datetime

# Configuración de Flask
app = Flask(__name__)

# Configuración de Redis
redis_host = os.environ.get("REDIS", "localhost")
redis_client = redis.Redis(host=redis_host, port=6379)

# Configuración de la API
api_url = "http://" + os.environ.get("API", "127.0.0.1:4000")

# Configuración de Celery
app.config['CELERY_BROKER_URL'] = 'redis://' + redis_host + ':6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://' + redis_host + ':6379/0'

# Inicialización de Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Definición de tareas de Celery
@celery.task(bind=True)
def deleteConfirm_as(self, uuid):
    headers = {'content-type': 'application/json'}
    r= R.get(api_url + "/confirmEmailDelete/" + uuid)
    return r.status_code, r.json()

@celery.task(bind=True)
def taskFinishedArticle(self, data):
    headers = {'x-access-tokens': data["token"]}
    r= R.put(api_url + "/articleFinish/" + data["article"], headers=headers)
    return r.status_code, r.json()

@celery.task(bind=True)
def taskStartedArticle(self, data):
    headers = {'x-access-tokens': data["token"]}
    r= R.put(api_url + "/articleStart/" + data["article"], headers=headers)
    return r.status_code, r.json()

@celery.task(bind=True)
def taskStartedAuction(self, data):
    headers = {'x-access-tokens': data["token"]}
    r= R.put(api_url + "/auctionsStart/" + data["article"], headers=headers)
    return r.status_code, r.json()

@celery.task(bind=True)
def taskFinishedAuction(self, data):
    headers = {'x-access-tokens': data["token"]}
    r= R.put(api_url + "/auctionFinished/" + data["article"], headers=headers)
    return r.status_code, r.json()

def deleteConfirm(data):
    deleteConfirm_as.apply_async(kwargs={"uuid": data["uuid"]}, countdown=24*60*60)

def finishedArticle(data):
    article_id = data["article"]
    time = data["time"]
    task_id = Articles().getTaskId(article_id)
    if task_id:
        celery.control.revoke(task_id, terminate=True, signal="SIGKILL")
    task = taskFinishedArticle.apply_async(kwargs={"data": data}, countdown=time)
    Articles().addArticle(article_id, str(task))

def startedArticle(data):
    article_id = data["article"]
    time = data["time"]
    task_id = Articles().getTaskId(article_id)
    if task_id:
        celery.control.revoke(task_id, terminate=True, signal="SIGKILL")
    task = taskStartedArticle.apply_async(kwargs={"data": data}, countdown=time)
    Articles().addArticle(article_id, str(task))

def startedAuction(data):
    article_id = data["article"]
    date_format="%d/%m/%YT%H:%M:%S%z"
    d=  datetime.datetime.strptime(data["time"], date_format)
    d=d.astimezone(datetime.timezone.utc)
    now=datetime.datetime.now()
    now=now.astimezone(datetime.timezone.utc)
    time= (d-now).total_seconds()
    if time <0:
        time=0
    task_id = Articles().getTaskId(article_id)
    if task_id:
        celery.control.revoke(task_id, terminate=True, signal="SIGKILL")
    task = taskStartedAuction.apply_async(kwargs={"data": data}, countdown=time)
    Articles().addArticle(article_id, str(task))

def finishedAuction(data):
    article_id = data["article"]
    date_format="%d/%m/%YT%H:%M:%S%z"
    d=  datetime.datetime.strptime(data["time"], date_format)
    d=d.astimezone(datetime.timezone.utc)
    now=datetime.datetime.now()
    now=now.astimezone(datetime.timezone.utc)
    time= (d-now).total_seconds()
    if time <0:
        time=0
    task_id = Articles().getTaskId(article_id)
    if task_id:
        celery.control.revoke(task_id, terminate=True, signal="SIGKILL")
    task = taskFinishedAuction.apply_async(kwargs={"data": data}, countdown=time)
    Articles().addArticle(article_id, str(task))


tasks = {
    "deleteConfirm": deleteConfirm,
    "finishedArticle": finishedArticle,
    "startedArticle": startedArticle,
    "startedAuction":startedAuction,
    "finishedAuction": finishedAuction

}

# Función para manejar mensajes de Redis
def handle_message(message):
    if message['type'] == 'message':
        data = json.loads(message['data'])
        task_name = data['task_name']
        if task_name in tasks:
            tasks[task_name](data)

# Suscripción a mensajes de Redis
def subscribe_to_redis():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(**{'task_channel': handle_message})
    print('Listening for messages on task_channel...')
    for message in pubsub.listen():
        if message['type'] == 'message':
            handle_message(message)

# Iniciar la suscripción a Redis en un hilo separado
def run_redis_subscriber():
    thread = threading.Thread(target=subscribe_to_redis)
    thread.start()

if __name__ == '__main__':
    run_redis_subscriber()
    from waitress import serve
    os.environ['FLASK_ENV'] = 'development' 
    serve(app, host="0.0.0.0", port=5000)
