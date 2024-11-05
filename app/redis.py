import json
import threading
import redis
from app.mediador import deleteConfirm, finishedArticle, startedArticle, startedAuction,finishedAuction



# Configuración de Redis
redis_host = os.environ.get("REDIS", "localhost")
redis_client = redis.Redis(host=redis_host, port=6379)

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