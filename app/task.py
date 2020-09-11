import requests
from app import db
from models import * 

def count_words(url):
    try:    
        resp = requests.get(url)
        output = len(resp.text.split())
        print(output)
        result = Result(url=url,output=output)
        db.session.add(result)
        db.session.commit()
        output ={"result":{"url":url,"output":output}}
    except:
        error = "some error occured while adding to db"
        output = {"error": error}
    return output