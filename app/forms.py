from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateTimeField, DateField, DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, length, URL, Optional
from app.models import Artist, Location, Porch, Porchfest


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
    image = StringField('Profile Image url', validators=[Optional()])
    spotify = StringField('Spotify url', validators=[Optional()])  # removed url check because was never accepting
    youtube = StringField('Youtube url', validators=[Optional()])  # removed url check because was never accepting
    facebook = StringField('Facebook url', validators=[Optional()])  # removed url check because was never accepting
    submit = SubmitField('Register')

    def validate_zip(self, zip):
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')

    def validate_spotify(self, spotify):
        # need to fix these to allow there to be no link entered
        if "spotify" not in spotify.data and spotify.data is not None:
            raise ValidationError('Please enter a url for Spotify')

    def validate_youtube(self, youtube):
        if "youtube" not in youtube.data and youtube.data is not None:
            raise ValidationError('Please enter a url for Youtube')

    def validate_facebook(self, facebook):
        if "facebook" not in facebook.data and facebook.data is not None:
            raise ValidationError('Please enter a url for Facebook')

    def validate_email(self, email):
        artist = Artist.objects(email=email.data).first()
        if artist is not None:
            raise ValidationError('Email already being used!')


class EditArtistForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    genre = StringField('Genre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        artist = Artist.objects(email=email.data).first()
        if artist is not None and current_user.email != artist.email:
            raise ValidationError('Email already being used!')


class PorchForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    porchfest_id = SelectField('Choose a Porchfest', validators=[DataRequired()])
    # maybe validate by checking address exists with map api
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[length(min=2, max=2, message="Length should be two letters!")])
    zip = StringField('Zip code', validators=[length(min=5, max=5, message="Should be 5 numbers long!")])
    startTime = DateTimeLocalField('Start time available', format='%Y-%m-%dT%H:%M', validators=[])
    endTime = DateTimeLocalField('End time available', format='%Y-%m-%dT%H:%M', validators=[])
    submit = SubmitField('Submit')

    def validate_zip(self, zip):
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')

    def validate_location(self, porchfest_id, city, state, zip):
        # think this id in the query may need to be the zip code because i believe that is what is serving as the id
        festLocation = Location.objects(zip_code=porchfest_id.data).first
        if festLocation.city != city.data or festLocation.state != state.data or festLocation.zip_code != zip.data:
            raise ValidationError('Location does not match the location of the selected Porchfest!')

    def validate_time(self, startTime, endTime, porchfest_id):
        if endTime.data < startTime.data:
            raise ValidationError('End time must be after start time')
        fest = Porchfest.objects(id=porchfest_id).first()
        if endTime.data < fest.start_time or endTime.data > fest.end_time:
            raise ValidationError('Times must be during Porchfest times')
        if startTime.data < fest.start_time or startTime.data > fest.end_time:
            raise ValidationError('Times must be during Porchfest times')



class ArtistPorchfestSignUpForm(FlaskForm):
    porchfest = SelectField('Choose a porchfest', validators=[DataRequired()], coerce=int)
    porch = BooleanField('I already have a porch')
    # can check that location matches with location of selected porchfest
    # maybe validate by checking address exists with map api
    # maybe keep this hidden unless the checkbox is clicked
    address = StringField('Address (if you have a porch)', validators=[])
    city = StringField('City (if you have a porch)', validators=[])
    state = StringField('State (if you have a porch)', validators=[length(min=0, max=2, message="Length should be two letters!")])
    zip = StringField('Zip code (if you have a porch)', validators=[length(min=0, max=5, message="Should be 5 numbers long!")])
    startTime = DateTimeLocalField('Start time available', format='%Y-%m-%dT%H:%M', validators=[])
    endTime = DateTimeLocalField('End time available', format='%Y-%m-%dT%H:%M', validators=[])
    submit = SubmitField('Submit')

    def validate_zip(self, zip):
        for c in zip.data:
            if c.isalpha():
                raise ValidationError('Zip code must consist of only integers')

    def validate_location(self, porchfest, city, state, zip):
        # think this id in the query may need to be the zip code because i believe that is what is serving as the id
        fest = Porchfest.objects(id=porchfest.data).first()
        festLocation = fest.location
        if festLocation.city != city.data or festLocation.state != state.data or festLocation.zip_code != zip.data:
            raise ValidationError('Location does not match the location of the selected Porchfest!')

    def has_porch_validator(self, address, city, state, zip, porch):
        if porch.data:
            if address.data == "":
                raise ValidationError('If you have a porch you must enter the address!')
            if city.data == "":
                raise ValidationError('If you have a porch you must enter the city!')
            if state.data == "":
                raise ValidationError('If you have a porch you must enter the state!')
            if zip.data == "":
                raise ValidationError('If you have a porch you must enter the zip code!')
        else:
            if address.data != "":
                raise ValidationError('Leave address blank if you do not have a porch yet!')
            if city.data != "":
                raise ValidationError('Leave city blank if you do not have a porch yet!')
            if state.data != "":
                raise ValidationError('Leave state blank if you do not have a porch yet!')
            if zip.data != "":
                raise ValidationError('Leave zip code blank if you do not have a porch yet!')




class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class FindAPorchfestForm(FlaskForm):
    porchfest = SelectField('Choose a Porchfest', validators=[DataRequired()], id='select_porchfest')
