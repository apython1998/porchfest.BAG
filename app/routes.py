from flask import render_template, url_for, redirect, flash, request, jsonify
from werkzeug.urls import url_parse
from app import app
from app.models import Artist, Porch, Porchfest, Show, Location
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import NewArtistForm, LoginForm, PorchForm, ArtistPorchfestSignUpForm, FindAPorchfestForm, EditArtistForm
from flask_googlemaps import GoogleMaps, Map
import requests


@app.route('/reset_db')
def reset_db():
    for location in Location.objects:
        location.delete()
    for artist in Artist.objects:
        artist.delete()
    for porch in Porch.objects:
        porch.delete()
    for fest in Porchfest.objects:
        fest.delete()
    for show in Show.objects:
        show.delete()
    times = [
        datetime(2018, 12, 26, 9, 0, 0),  # start for porchfests
        datetime(2018, 12, 26, 17, 0, 0),  # end for porchfests
        datetime(2018, 12, 26, 12, 0, 0),  # first show end time
        datetime(2018, 12, 26, 15, 0, 0)  # second show end time
    ]
    default_locations = [
        Location(city='Ithaca', state='NY', zip_code='14850'),
        Location(city='Binghamton', state='NY', zip_code='13901'),
        Location(city='Albany', state='NY', zip_code='12203'),
        Location(city='Winchester', state='MA', zip_code='01890')
    ]
    for location in default_locations:
        location.save(cascade=True)
    default_porches = [
        Porch(name='Ithaca Porch 1', email='ithacaPorch1@email.com', address='953 Danby Rd',
              location=Location.objects(city='Ithaca', state='NY').first(), time_available_start=times[0],
              time_available_end=times[1], lat=42.4199351, long=-76.4969643),
        Porch(name='Ithaca Porch 2', email='ithacaPorch2@email.com', address='123 Ithaca Rd',
              location=Location.objects(city='Ithaca', state='NY').first(), time_available_start=times[0],
              time_available_end=times[1], lat=42.438657, long=-76.4800496)
    ]
    for porch in default_porches:
        porch.save(cascade=True)
    default_artists = [
        Artist(email='artist1@email.com', name='Artist 1', description='artist 1 desc',
               media_links=['https://www.spotify.com/artist1'],
               location=Location.objects(city='Ithaca', state='NY').first(),
               image='https://miquon.org/wp-content/uploads/2016/02/GenericUser.png'),
        Artist(email='artist2@email.com', name='Artist 2', description='artist 2 desc',
               media_links=['https://myspotify.com'], location=Location.objects(city='Albany', state='NY').first())
    ]
    for artist in default_artists:
        artist.set_password('default')
        artist.save(cascade=True)
    default_shows = [
        Show(artist=Artist.objects(name='Artist 1').first(), porch=Porch.objects(name='Ithaca Porch 1').first(),
             start_time=times[0], end_time=times[2]),
        Show(artist=Artist.objects(name='Artist 1').first(), porch=Porch.objects(name='Ithaca Porch 2').first(),
             start_time=times[2], end_time=times[3]),
    ]
    for show in default_shows:
        show.save(cascade=True)
    default_porchfests = [
        Porchfest(location=Location.objects(city='Ithaca', state='NY').first(), start_time=times[0], end_time=times[1],
                  porches=[Porch.objects(name='Ithaca Porch 1').first(), Porch.objects(name='Ithaca Porch 2').first()],
                  shows=[Show.objects(artist=Artist.objects(name='Artist 1').first()).first()]),
        Porchfest(location=Location.objects(city='Binghamton', state='NY').first(), start_time=times[0], end_time=times[1]),
        Porchfest(location=Location.objects(city='Albany', state='NY').first(), start_time=times[0], end_time=times[1])
    ]
    for porchfest in default_porchfests:
        porchfest.save(cascade=True)
    flash("Database has been reset!")
    return render_template('index.html')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/find_a_porchfest')
def findaporchfest():
    default = Porchfest.objects(location=Location.objects(zip_code='14850').first()).first()
    form = FindAPorchfestForm(porchfest=default.id)
    markers = []
    for p in default.porches:
        markers.append((p.lat, p.long))
    # need a default lat and long for each fest to not crash if there are no porches
    myMap = Map(
        identifier="view_side",
        lat=markers[0].lat,
        lng=-76.4951,
        markers=[]
    )
    return render_template('findaporchfest.html', form=form, mymap=myMap)


@app.route('/_artists_for_porchfest') # restful lookup for findaporchfest page
def artists_for_porchfest():
    porchfest_id = request.args.get('porchfestID', '')
    porchfest = Porchfest.objects.get(id=porchfest_id)
    porchfest_artists = []
    for show in porchfest.shows:
        artist_name = show.artist.name
        if artist_name not in porchfest_artists:
            porchfest_artists.append(artist_name)
    return jsonify(porchfest_artists)


@app.route('/artist/<artist_name>')
def artist(artist_name):
    artist = Artist.objects(name=artist_name).first_or_404()
    shows_for_artist = Show.objects(artist=artist, start_time__gt=datetime.utcnow)
    return render_template('artist.html', artist=artist, shows=shows_for_artist)


@login_required
@app.route('/edit_artist', methods=['GET', 'POST'])
def edit_artist():
    if current_user._class_name is 'Artist':
        form = EditArtistForm()
        if form.validate_on_submit():
            current_user.email = form.email.data
            current_user.genre = form.genre.data
            current_user.description = form.description.data
            current_user.save(cascade=True)
            flash('Artist info has been updated successfully')
            return redirect(url_for('artist', artist_name=current_user.name))
        elif request.method == 'GET':
            form.email.data = current_user.email
            form.genre.data = current_user.genre
            form.description.data = current_user.description
        return render_template('signUp.html', form=form)
    else:
        flash("You are not authorized to edit artist info!")
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def signUp():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = NewArtistForm()
    if form.validate_on_submit():
        # make new artist
        location = Location.objects(city=form.city.data, state=form.state.data).first()
        if location is None:
            location = Location(city=form.city.data, state=form.state.data, zip_code=form.zip.data)
            location.save(cascade=True)
        mediaLinks = []
        if form.facebook.data != "":
            mediaLinks.append(form.facebook.data)
        if form.youtube.data != "":
            mediaLinks.append(form.youtube.data)
        if form.spotify.data != "":
            mediaLinks.append(form.spotify.data)
        newArtist = Artist(email=form.email.data, name=form.bandName.data, description=form.description.data,
                           media_links=mediaLinks, location=location, genre=form.genre.data, image=form.image.data)
        newArtist.set_password(form.password.data)
        newArtist.save(cascade=True)
        return redirect(url_for('logIn'))  # probably want to send to artist page once that exists
    return render_template('signUp.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def logIn():
    if current_user.is_authenticated:
        #  flash("You are logged in!")
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Artist.objects(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('logIn'))
        login_user(user, remember=form.remember_me.data)
        flash('Login successful')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).necloc != '':
            next_page = url_for('index')  # maybe change this to artist's page
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/new_porch', methods=['GET', 'POST'])
def addPorch():
    form = PorchForm()
    porchfests = Porchfest.objects()
    form.porchfest_id.choices = [(p.location.zip_code, p.location.city+", "+p.location.state+" "+p.start_time.strftime("%m-%d-%Y %H:%M")+" to "+p.end_time.strftime("%m-%d-%Y %H:%M")) for p in porchfests]
    if form.validate_on_submit():
        flash('Porch added!')
        flash(form.startTime.data > form.endTime.data)
        location = Location.objects(city=form.city.data, state=form.state.data).first()
        if location is None:
            location = Location(city=form.city.data, state=form.state.data, zip_code=form.zip.data)
            location.save(cascade=True)
        newPorch = Porch(name=form.name.data, email=form.email.data, address=form.address.data, location=location, time_available_start=form.startTime.data, time_available_end=form.endTime.data)
        newPorch.save(cascade=True)
        porchfest = Porchfest.objects(location=location.id).first()
        porchfest.porches.append(newPorch)
        porchfest.save(cascade=True)
        return redirect(url_for('index'))
    return render_template('addPorch.html', form=form)


@login_required
@app.route('/sign_up', methods=['GET', 'POST'])
def artistFestSignUp():
    form = ArtistPorchfestSignUpForm()
    porchfests = Porchfest.objects()
    form.porchfest.choices = [(p.location.zip_code, p.location.city + ", " + p.location.state+" "+p.start_time.strftime("%m-%d-%Y %H:%M")+" to "+p.end_time.strftime("%m-%d-%Y %H:%M")) for p in porchfests]
    if form.validate_on_submit():
        flash('Signed up for '+form.city.data+", "+form.state.data+" porchfest!")
        artist = Artist.objects(name=current_user.__name__).first()
        location = Location.objects(zip_code=form.zip.data).first()
        if form.porch.data:
            porch = Porch.objects(address=form.address.data).first()
            if porch is None:
                porch = Porch(name=form.porch_owner.data, email=form.porch_email.data, address=form.address.data, location=location, time_available_start=form.startTime.data, time_available_end=form.endTime.data)
                porch.save(cascade=True)
        else:
            porch = None
        show = Show(artist=artist, porch=porch, start_time=form.startTime.data, end_time=form.startTime.data)
        show.save(cascade=True)
        return redirect(url_for('index'))
    return render_template('artistToPorch.html', form=form)


""""
    form.porchfest.choices = [("", "---")] + [(p.id, p.location.city + ', ' + p.location.state) for p in Porchfest.objects()]
    myPorch = Porch.objects(name="Ithaca Porch 2").first()
    address = myPorch.address.split(' ')
    reqStr = "https://maps.googleapis.com/maps/api/geocode/json?address="
    for i in address:
        reqStr = reqStr+i+"+"
    reqStr = reqStr[:-1]
    reqStr = reqStr+myPorch.location.city+",+"+myPorch.location.state+"&key=AIzaSyCYzkoBrnmcTkdPO6l8IHyPo7PZOAgeg-4"
    res = requests.get(reqStr)
    resJSON = res.json()
    data = resJSON['results'][0]
    lat = data['geometry']['location']['lat']
    long = data['geometry']['location']['lng']
    flash(str(lat)+", "+str(long))
"""