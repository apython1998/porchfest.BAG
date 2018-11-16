from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login


class Location(db.Document):
    city = db.StringField()
    state = db.StringField()
    zip_code = db.StringField(max_length=5)

    def __repr__(self):
        return '<Location {}, {}>'.format(self.city, self.state)


class Artist(UserMixin, db.Document):
    email = db.StringField()
    password_hash = db.StringField()
    name = db.StringField()
    description = db.StringField()
    media_links = db.ListField(db.URLField())
    location = db.ReferenceField(Location)

    def __repr__(self):
        return '<Artist {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Porch(db.Document):
    name = db.StringField()
    email = db.StringField()
    address = db.StringField()
    location = db.ReferenceField(Location)
    time_available_start = db.DateTimeField(default=datetime.utcnow)
    time_available_end = db.DateTimeField(default=datetime.utcnow)

    def __repr__(self):
        return '<Porch {}>'.format(self.name)


class Show(db.Document):
    artist = db.ReferenceField(Artist)
    porch = db.ReferenceField(Porch)
    start_time = db.DateTimeField(default=datetime.utcnow)
    end_time = db.DateTimeField(default=datetime.utcnow)

    def __repr__(self):
        return '<Show {} playing @ {}>'.format(self.artist.name, self.porch.address)


class Porchfest(db.Document):
    location = db.ReferenceField(Location)
    start_time = db.DateTimeField(default=datetime.utcnow)
    end_time = db.DateTimeField()
    porches = db.ListField(db.ReferenceField(Porch, reverse_delete_rule=db.CASCADE))
    shows = db.ListField(db.ReferenceField(Show, reverse_delete_rule=db.CASCADE))

    def __repr__(self):
        return '<Porchfest in {}, {}>'.format(self.location.city, self.location.state)
