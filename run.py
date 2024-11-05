
import os
from flask import Flask
from app.redis import run_redis_subscriber

app = Flask(__name__)


if __name__ == '__main__':
    run_redis_subscriber()
    from waitress import serve
    os.environ['FLASK_ENV'] = 'development' 
    serve(app, host="0.0.0.0", port=5000)
