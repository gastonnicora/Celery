from flask import Flask,request ,render_template, \
    url_for, jsonify
from celery import Celery
import requests as R


app = Flask(__name__)


# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'


# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task(bind=True)
def hola_as(self,referer):
    r=R.get(referer+"/chau")
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
@app.route('/hola')
def hola():
    referer=request.headers.get("Referer")
    link,r= url(referer)
    if(r==404):
        return jsonify({"error":"La url esta mal"}),404 
    hola_as.apply_async(kwargs={'referer':link},countdown=10) 
    return jsonify({"sms":"hola"}),202 

if __name__ == '__main__':
    app.run(debug=True)
