from flask import Flask,request ,render_template, \
    url_for, jsonify
from celery import Celery
import requests as R
from os import environ
from session import Session


app = Flask(__name__)

redis= environ.get("REDIS","localhost")
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://'+redis+':6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://'+redis+':6379/0'


# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



@celery.task(bind=True)
def deleteConfirm_as(self,referer,uuid, token):
    headers = {"X-Access-Tokens":token}
    r=R.get(referer+"/confirmEmailDelete/"+uuid,headers=headers)
    print(r)
    print(r.content)


def url(referer):
    r=None
    try:

        link="https://"+referer
        r=R.get(link+"/ping")
        return link,202
    except:
        try:
            link="http://"+referer
            r=R.get(link+"/ping")
            return link,202
        except:
            return None,404


@app.route('/deleteConfirm/<string:uuid>')
def deleteConfirm(uuid):
    api= request.headers.get("Referer")
    link,r= url(api)
    if(r==404):
        return jsonify({"error":"La url esta mal o el servidor desconectado"}),404 
    
    token = Session().getHost(api)
    deleteConfirm_as.apply_async(kwargs={'referer':link,"uuid":uuid,"token":token},countdown=30) 
    return jsonify({"sms":"hola"}),202 

@app.route("/ping")  
def ping():
    return jsonify({}),202

@app.route("/login")  
def login():
    Session().addHost(request.headers.get("Referer"),request.headers.get("X-Access-Tokens"))
    return jsonify({}),202

if __name__ == '__main__':
    # from waitress import serve
    app.run(host="0.0.0.0", port=5000, debug=True)
    # serve(app, host="0.0.0.0", port=5000)
 