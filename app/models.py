from datetime import datetime
from sqlalchemy import UniqueConstraint
from hashlib import md5
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import app, db, login


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(256), index=True)
    state = db.Column(db.String(64), index=True)
    zip_code = db.Column(db.Integer, index=True)

    __table_args__ = (UniqueConstraint('city', 'state', 'zip_code', name='uniqueLocation'),)

    def __repr__(self):
        return '<Location {}, {}>'.format(self.city, self.state)


class Porchfest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, default=datetime.utcnow)
    porches = db.relationship('Porch', backref='porches', lazy='dynamic')

    __table_args__ = (UniqueConstraint('location_id', 'start_time', name='uniquePorchfest'),)

    def __repr__(self):
        return '<Porchfest in {}, {}>'.format(self.location_id.city, self.location_id.state)


class Artist(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(128), index=True, unique=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    description = db.Column(db.String(256), index=True)
    spotify_url = db.Column(db.String(256))
    youtube_url = db.Column(db.String(256))
    facebook_url = db.Column(db.String(256))
    playing = db.relationship('ArtistToPorch', backref='shows', lazy='dynamic')

    def __repr__(self):
        return '<Artist {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Porch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    email = db.Column(db.String(256))
    address = db.Column(db.String(256))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    porchfest_id = db.Column(db.Integer, db.ForeignKey('porchfest.id'))
    time_available_start = db.Column(db.DateTime, default=datetime.utcnow)
    time_available_end = db.Column(db.DateTime, default=datetime.utcnow)
    hosting = db.relationship('Artist', secondary='artist_to_porch')

    __table_args__ = (UniqueConstraint('address', 'location_id', 'porchfest_id', name='uniquePorch'),)

    def __repr__(self):
        return '<Porch {}>'.format(self.name)


class ArtistToPorch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    porch_id = db.Column(db.Integer, db.ForeignKey('porch.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, default=datetime.utcnow)
    artist = db.relationship('Artist', backref='artist')
    porch = db.relationship('Porch', backref='porch')
