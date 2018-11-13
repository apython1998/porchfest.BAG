from flask import render_template, url_for, redirect, flash, request
from app import app, db
from app.models import Artist, Porch, Porchfest, ArtistToPorch, Location
from datetime import datetime


@app.route('/reset_db')
def reset_db():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()
    times = [
        datetime(2018, 9, 26, 9, 0, 0),  # start for porchfests
        datetime(2018, 9, 26, 17, 0, 0),  # end for porchfests
        datetime(2018, 9, 26, 12, 0, 0),  # first show end time
        datetime(2018, 9, 26, 15, 0, 0),  # second show end time
    ]
    default_locations = [
        Location(city='Ithaca', state='NY', zip_code=14850),
        Location(city='Binghamton', state='NY', zip_code=13901),
        Location(city='Albany', state='NY', zip_code=12203)
    ]
    default_porchfests = [
        Porchfest(location_id=1, start_time=times[0], end_time=times[1]),
        Porchfest(location_id=2, start_time=times[0], end_time=times[1]),
        Porchfest(location_id=3, start_time=times[0], end_time=times[1])
    ]
    default_porches = [
        Porch(name='Ithaca Porch 1', email='ithacaPorch1@email.com', address='953 Danby Rd', location_id=1,
              porchfest_id=1, time_available_start=times[0], time_available_end=times[1]),
        Porch(name='Ithaca Porch 2', email='ithacaPorch2@email.com', address='123 Ithaca Rd', location_id=1,
              porchfest_id=1, time_available_start=times[0], time_available_end=times[1])
    ]
    default_artists = [
        Artist(name='Artist 1', location_id=1, description='Artist 1 description'),
        Artist(name='Artist 2', location_id=1, description='Artist 2 description'),
        Artist(name='Artist 3', location_id=1, description='Artist 3 description')
    ]
    default_AToP = [
        ArtistToPorch(artist_id=1, porch_id=1, start_time=times[0], end_time=times[2]),
        ArtistToPorch(artist_id=2, porch_id=1, start_time=times[2], end_time=times[3]),
        ArtistToPorch(artist_id=3, porch_id=2, start_time=times[3], end_time=times[1])
    ]
    db.session.add_all(default_locations)
    db.session.add_all(default_porchfests)
    db.session.add_all(default_porches)
    db.session.add_all(default_artists)
    db.session.add_all(default_AToP)
    db.session.commit()

    # Here is some code to test it
    porchfest1 = Porchfest.query.get(1)
    for porch in porchfest1.porches:
        for artist in porch.hosting:
            print("{} is playing at {}".format(artist.name, porch.name))
    return render_template('index.html')

