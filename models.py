from db import db
class User(db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    user_name=db.Column(db.String)
    user_email=db.Column(db.String,unique=True)
    user_password=db.Column(db.String)

