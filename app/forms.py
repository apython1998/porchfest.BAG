from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateTimeField, DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, length, URL
from app.models import Artist, Location, Porch, Porchfest


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_check = PasswordField('Reenter Password', validators=[DataRequired(), EqualTo('password')])
    # might be able to just get rid of these since users do not have accounts at this time
    # and event coordinator registration will be hidden
    band = BooleanField('I have a band')
    event = BooleanField('I am an event coordinator')
    submit = SubmitField('Register')

    def validate_email(self, email):
        artist = Artist.query.filter_by(email=email.data).first()
        if artist is not None:
            raise ValidationError('Email already being used!')


class NewArtistForm(FlaskForm):
    bandName = StringField('Band Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_check = PasswordField('Reenter Password', validators=[DataRequired(), EqualTo('password')])
    genre = StringField('Genre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[length(min=2, max=2, message="Length should be two letters!")])
    zip = StringField('Zip code', validators=[length(min=5, max=5, message="Should be 5 numbers long!")])
    spotify = StringField('Spotify url', validators=[URL()])  # check if link is spotify
    youtube = StringField('Youtube url', validators=[URL()])  # check if link is youtube
    facebook = StringField('Facebook url', validators=[URL()])  # check if link is fb
    submit = SubmitField('Submit')

    def validate_zip(self, zip):
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')

    def validate_spotify(self, spotify):
        if "spotify" not in spotify.data:
            raise ValidationError('Please enter a url for Spotify')

    def validate_youtube(self, youtube):
        if "youtube" not in youtube.data:
            raise ValidationError('Please enter a url for Youtube')

    def validate_facebook(self, facebook):
        if "facebook" not in facebook.data:
            raise ValidationError('Please enter a url for Facebook')

    def validate_email(self, email):
        artist = Artist.query.filter_by(email=email.data).first()
        if artist is not None:
            raise ValidationError('Email already being used!')


class PorchForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    porchfest_id = SelectField('Choose a Porchfest', validators=[DataRequired()], coerce=int)
    # can check that location matches with location of selected porchfest
    # maybe validate by checking address exists with map api
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[length(min=2, max=2, message="Length should be two letters!")])
    # can have validator to check that each character is an integer
    zip = StringField('Zip code', validators=[length(min=5, max=5, message="Should be 5 numbers long!")])
    # can check here for 1) if there is a porchfest in that area 2) if the dates are within
    startTime = DateTimeField('Start time available', validators=[DataRequired()])
    endTime = DateTimeField('End time available', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_zip(self, zip):
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')

    def validate_time(self, startTime, endTime):
        if endTime.data < startTime.data:
            raise ValidationError('End time must be after start time')
        # get the start and end time for the porchfest and make sure entered times are between those


class ArtistPorchfestSignUpForm(FlaskForm):
    porchfest = SelectField('Choose a porchfest', validators=[DataRequired()], coerce=int)
    porch = BooleanField('I already have a porch')
    # can check that location matches with location of selected porchfest
    # maybe validate by checking address exists with map api
    # maybe keep this hidden unless the checkbox is clicked
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[length(min=2, max=2, message="Length should be two letters!")])
    zip = StringField('Zip code', validators=[length(min=5, max=5, message="Should be 5 numbers long!")])
    submit = SubmitField('Submit')

    def validate_zip(self, zip):
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
