import json
from flask import Flask,request , jsonify
from celery import Celery
import requests as R
from os import environ
from article import Articles


app = Flask(__name__)

redis= environ.get("REDIS","localhost")
api= environ.get("API","http://localhost:4000")
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://'+redis+':6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://'+redis+':6379/0'


# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task(bind=True)
def deleteConfirm_as(self,uuid):
    r=R.get(api+"/confirmEmailDelete/"+uuid)

@celery.task(bind=True)
def taskFinishedArticle(self,uuid):
    r=R.put(api+"/articleFinish/"+uuid)
    

@celery.task(bind=True)
def taskStartedArticle(self,uuid):
    r=R.put(api+"/articleStart/"+uuid)
    
    



@app.route('/deleteConfirm/<string:uuid>')
def deleteConfirm(uuid):
    deleteConfirm_as.apply_async(kwargs={"uuid":uuid},countdown=24*60*60) 
    return jsonify({"sms":"hola"}),202 


@app.route("/finishedArticle",methods=["POST"])
def finishedArticle():
    data= request.get_json()
    id = Articles().getTaskId(data.get("article"))
    if  id != None:
        celery.control.revoke(id,terminate=True,signal="SIGKILL")
    task=taskFinishedArticle.apply_async(kwargs={"uuid":data.get("article")},countdown=data.get("time")) 
    Articles().addArticle(data.get("article"),str(task))
    return jsonify({"sms":"hola"}),202 

@app.route("/startedArticle",methods=["POST"])
def startedArticle():
    data= request.get_json()
    id = Articles().getTaskId(data.get("article"))
    if  id != None:
        celery.control.revoke(id,terminate=True,signal="SIGKILL")
    task=taskStartedArticle.apply_async(kwargs={"uuid":data.get("article")},countdown=data.get("time")) 
    Articles().addArticle(data.get("article"),str(task))
    return jsonify({"sms":"hola"}),202 


if __name__ == '__main__':
    from waitress import serve
    # app.run(host="0.0.0.0", port=5000, debug=True)
    serve(app, host="0.0.0.0", port=5000)
 