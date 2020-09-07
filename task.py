import requests
from app import db
from models import * 

def count_words(url):
    resp = requests.get(url)
    output = len(resp.text.split())
    result = Result(url=url,output=output)
    db.session.add(result)
    db.session.commit()
    output = {"url":url,"output":output}
    return output