from app import db

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(100),unique=True, nullable=False)
    output = db.Column(db.String(100),nullable=False)

    def __init__(self, url, output):
        self.url = url
        self.output = output

    def __repr__(self):
        return '<id {}>'.format(self.id)


