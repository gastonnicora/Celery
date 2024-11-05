
from celery import Celery
import requests as R
import os


redis_host = os.environ.get("REDIS", "localhost")
# Inicialización de Celery
celery = Celery(__name__, broker='redis://' + redis_host + ':6379/0')
celery.conf.update(
        result_backend='redis://' + os.environ.get("REDIS", "localhost") + ':6379/0',
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
    )

# Configuración de la API
api_url = "http://" + os.environ.get("API", "127.0.0.1:4000")
# Definición de tareas de Celery

@celery.task(bind=True)
def deleteConfirm_as(self, uuid):
    headers = {'content-type': 'application/json'}
    try:
        r = R.get(api_url + "/confirmEmailDelete/" + uuid)
        r.raise_for_status()  
        return r.status_code, r.json()
    except Exception as e:
        print(f"Error al hacer la solicitud DELETE Confirm: {str(e)}")
        return 500, str(e)  
    
@celery.task(bind=True)
def taskFinishedArticle(self, data):
    headers = {'x-access-tokens': data["token"]}
    try:
        r = R.put(api_url + "/articleFinish/" + data["article"], headers=headers)
        r.raise_for_status()
        return r.status_code, r.json()
    except Exception as e:
        print(f"Error al hacer la solicitud PUT Finished Article: {str(e)}")
        return 500, str(e)

@celery.task(bind=True)
def taskStartedArticle(self, data):
    headers = {'x-access-tokens': data["token"]}
    try:
        r = R.put(api_url + "/articleStart/" + data["article"], headers=headers)
        r.raise_for_status()
        return r.status_code, r.json()
    except Exception as e:
        print(f"Error al hacer la solicitud PUT Started Article: {str(e)}")
        return 500, str(e)

@celery.task(bind=True)
def taskStartedAuction(self, data):
    headers = {'x-access-tokens': data["token"]}
    try:
        r = R.put(api_url + "/auctionStart/" + data["article"], headers=headers, timeout=30)
        r.raise_for_status()
        return r.status_code, r.json()
    except Exception as e:
        print(f"Error al hacer la solicitud PUT Started Auction: {str(e)}")
        return 500, str(e)

@celery.task(bind=True)
def taskFinishedAuction(self, data):
    headers = {'x-access-tokens': data["token"]}
    try:
        r = R.put(api_url + "/auctionFinished/" + data["article"], headers=headers)
        r.raise_for_status()
        return r.status_code, r.json()
    except Exception as e:
        print(f"Error al hacer la solicitud PUT Finished Auction: {str(e)}")
        return 500, str(e)

@celery.task(bind=True)
def taskFinishedAuction(self, data):
    headers = {'x-access-tokens': data["token"]}
    r= R.put(api_url + "/auctionFinished/" + data["article"], headers=headers)
    try:
        return r.status_code, r.json()
    except:
        return r.status_code, r.text
