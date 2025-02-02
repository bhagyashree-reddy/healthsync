from app import db
from flask_login import UserMixin

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(50))

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'
    


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.LargeBinary(length=(2**32)-1), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<Event {self.image_name}>"

    def __init__(self, image_name, image_data, description):
        self.image_name = image_name
        self.image_data = image_data
        self.description = description


class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    name = db.Column(db.String(100),unique=True, nullable=False)
    designation = db.Column(db.String(100), nullable=False)  # Add this line
    qualification=db.Column(db.String(100), nullable=False) 
    age = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer, nullable=False)

    def __init__(self, image_name, image_data, name, designation,qualification, age, experience):
        self.image_name = image_name
        self.image_data = image_data
        self.name = name
        self.designation = designation
        self.qualification=qualification
        self.age = age
        self.experience = experience

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


