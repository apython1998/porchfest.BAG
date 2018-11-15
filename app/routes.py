from flask import render_template, url_for, redirect, flash, request
from app import app
from app.models import Artist, Porch, Porchfest, Show, Location
from datetime import datetime


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
    times = [
        datetime(2018, 9, 26, 9, 0, 0),  # start for porchfests
        datetime(2018, 9, 26, 17, 0, 0),  # end for porchfests
        datetime(2018, 9, 26, 12, 0, 0),  # first show end time
        datetime(2018, 9, 26, 15, 0, 0)  # second show end time
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
              time_available_end=times[1]),
        Porch(name='Ithaca Porch 2', email='ithacaPorch2@email.com', address='123 Ithaca Rd',
              location=Location.objects(city='Ithaca', state='NY').first(), time_available_start=times[0],
              time_available_end=times[1])
    ]
    for porch in default_porches:
        porch.save(cascade=True)
    default_artists = [
        Artist(email='artist1@email.com', name='Artist 1', description='artist 1 desc', media_links=[],
               location=Location.objects(city='Ithaca', state='NY').first()),
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
                  shows=[Show.objects(artist=Artist.objects(name='Artist 1').first()).first()]),
        Porchfest(location=Location.objects(city='Binghamton', state='NY').first(), start_time=times[0], end_time=times[1]),
        Porchfest(location=Location.objects(city='Albany', state='NY').first(), start_time=times[0], end_time=times[1])
    ]
    for porchfest in default_porchfests:
        porchfest.save(cascade=True)
    return render_template('index.html')
