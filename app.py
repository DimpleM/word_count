import os
from flask import Flask
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
        if validate_url(request.form.get("url")) == True:
            res = Result.query.filter_by(url=request.form.get("url")).first()
            print(res)
            if res == None:
                try:
                    url = request.form.get("url")
                    job = queue.enqueue_call(
                        count_words, args=(url,)
                    )
                    job = Job.fetch(job.get_id(), connection=conn)
                    time.sleep(2)
                    if job.is_finished:
                        result =  job.result
                    else:
                        error = "Some Error Occured"
                
                    print(job.is_finished)
                    print(job.result)
                except:
                    error = "Some error occured"
            else: 
                result = res.__dict__
        else:
            error = "Please enter a valid user"
    return render_template("home.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
