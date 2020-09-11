import os
from flask import Flask, url_for, redirect
from flask import render_template
from flask import request
import requests
from flask_sqlalchemy import SQLAlchemy
import re
from rq import Queue
from rq.job import Job
from worker import conn
from flask import jsonify
import time
from flask_api import status
import time
from functools import wraps

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "word_count.db"))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
queue = Queue(connection=conn)

from task import *
from models import *

def validate_url(url):
    url = url or 'invalid'
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    is_valid = re.match(regex, url) is not None
    return is_valid



@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    error = ''
    if request.method == 'POST':
        if validate_url(request.form.get("url")) == True and request.form.get("url")!= '':
            res = Result.query.filter_by(url=request.form.get("url")).first()
            if res == None:
                url = request.form.get("url")
                job = queue.enqueue_call(
                    count_words, args=(url,)
                )
                job = Job.fetch(job.get_id(), connection=conn)
                return redirect(url_for('get_results', job_key=job.get_id()))
            else: 
                result = res.__dict__
                return render_template("home.html", result=result)
        else:
            return render_template("home.html",result = {},error="Invalid URL"),status.HTTP_400_BAD_REQUEST
    return render_template("home.html",result=result)

def retry(ExceptionToCheck, tries=4, delay=1, backoff=2, logger=None):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print( msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry


@app.route("/results/<job_key>", methods=['GET'])
@retry(Exception, tries=4)
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        result = job.result
        if "result" in result.keys():
            return render_template("home.html", result=result['result'])
        else:
            return render_template("home.html", error=result["error"]), status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        raise Exception("202")
   
if __name__ == "__main__":
    app.run(host='0.0.0.0')
