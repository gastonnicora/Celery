
from article import Articles
import datetime
from app.celery import deleteConfirm_as, celery, taskFinishedArticle, taskFinishedAuction,taskStartedArticle, taskStartedAuction


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
