from app import db
from flask_login import UserMixin
from datetime import datetime


# class Contact(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50), nullable=False)
#     last_name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     subject = db.Column(db.String(100), nullable=False)
#     contact_number = db.Column(db.String(15), nullable=False)
#     city = db.Column(db.String(50))

#     def __repr__(self):
#         return f'<Contact {self.first_name} {self.last_name}>'



class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(100), nullable=False)
    image_data = db.Column(db.LargeBinary(length=(2**32)-1), nullable=False)

    def __init__(self, image_name, image_data):
        self.image_name = image_name
        self.image_data = image_data


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<user : {self.username}>'


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    image_name = db.Column(db.String(255), nullable=True)  # Store image filename
    image_data = db.Column(db.LargeBinary(length=(2**32)-1), nullable=True)  # Store image data as binary
 # Store filename  # Path to the image


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    service_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100))
    contact_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    amount = db.Column(db.Float, nullable=False)




