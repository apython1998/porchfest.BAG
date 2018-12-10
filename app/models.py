from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login


class Location(db.Document):
    city = db.StringField()
    state = db.StringField()
    zip_code = db.StringField(max_length=5)
    meta = {
        'indexes': [
            {'fields': ('city', 'state', 'zip_code'), 'unique': True}
        ]
    }

    def __repr__(self):
        return '<Location {}, {}>'.format(self.city, self.state)


class Artist(UserMixin, db.Document):
    email = db.StringField(unique=True)
    password_hash = db.StringField()
    name = db.StringField(unique=True)
    description = db.StringField()
    media_links = db.ListField(db.StringField())
    location = db.ReferenceField(Location)
    image = db.StringField()
    genre = db.StringField()

    def __repr__(self):
        return '<Artist {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return Artist.objects(id=id).first()


class Porch(db.Document):
    name = db.StringField()
    email = db.StringField(unique=True)
    address = db.StringField()
    location = db.ReferenceField(Location)
    time_slots = db.ListField(db.DateTimeField())
    lat = db.FloatField()
    long = db.FloatField()
    meta = {
        'indexes': [
            {'fields': ('address', 'location'), 'unique': True}
        ]
    }

    def __repr__(self):
        return '<Porch {}>'.format(self.name)


class Show(db.Document):
    artist = db.ReferenceField(Artist)
    porch = db.ReferenceField(Porch)
    start_time = db.DateTimeField(default=datetime.utcnow)
    end_time = db.DateTimeField(default=datetime.utcnow)
    meta = {
        'indexes': [
            {'fields': ('artist', 'porch'), 'unique': True}
        ]
    }

    def __repr__(self):
        return '<Show {} playing @ {}>'.format(self.artist.name, self.porch.address)


class Porchfest(db.Document):
    location = db.ReferenceField(Location)
    start_time = db.DateTimeField(default=datetime.utcnow)
    end_time = db.DateTimeField(default=datetime.utcnow)
    porches = db.ListField(db.ReferenceField(Porch, reverse_delete_rule=db.CASCADE))
    shows = db.ListField(db.ReferenceField(Show, reverse_delete_rule=db.CASCADE))
    meta = {
        'indexes': [
            {'fields': ('location', 'start_time'), 'unique': True}
        ]
    }

    def __repr__(self):
        return '<Porchfest in {}, {}>'.format(self.location.city, self.location.state)
