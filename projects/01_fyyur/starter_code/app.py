#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
from json import dump
from sre_parse import State
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = "Show"
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    # artists : relationship mamyTomany with artist through show
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self) -> str:
        return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city} >'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    # venues : relationship mamyTomany with venue through show
    shows = db.relationship('Show', backref='artist', lazy=True)


# TODO: implement any missing fields, as a database migration using Flask-Migrate
migrate = Migrate(app, db)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venueStates = db.session.query(Venue.state, Venue.city, db.func.count(Venue.id)).group_by(
        Venue.city, Venue.state).order_by(Venue.state).all()

    data = []
    for venueState in venueStates:
        venues = Venue.query.filter_by(city=venueState.city).all()
        allvenues = []
        for venue in venues:
            allvenues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.query.filter(
                    Show.venue_id == venue.id, Show.start_time >= datetime.today()).count()
            })
        data.append({
            "city": venueState.city,
            "state": venueState.state,
            "venues": allvenues
        })

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')

    venuesquery = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))

    data = []

    for venue in venuesquery.all():
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Show.query.filter(
                Show.venue_id == venue.id, Show.start_time >= datetime.today()).count()
        })

    response = {
        "count": venuesquery.count(),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)

    # get the list of shows with venue_id and the start_time is to come
    showquery = Show.query.filter(
        Show.venue_id == venue_id, Show.start_time >= datetime.today())

    # get the list of shows with venue_id and the start_time is passed
    pastshowquery = Show.query.filter(
        Show.venue_id == venue_id, Show.start_time < datetime.today())

    # structure the result as it is intended from the view
    pastshows = []
    artistShow = []

    for show in showquery.all():
        artistShow.append({
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    for show in pastshowquery.all():
        pastshows.append({
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    data = {
        "id": venue_id,
        "name": venue.name,
        "genres": venue.genres[1:-1].split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": pastshows,
        "upcoming_shows": artistShow,
        "past_shows_count": len(pastshows),
        "upcoming_shows_count": len(artistShow),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate_on_submit():
        newvenu = Venue(name=form.name.data,
                        city=form.city.data, state=form.state.data,
                        genres=form.genres.data, address=form.address.data,
                        phone=form.phone.data, image_link=form.image_link.data,
                        facebook_link=form.facebook_link.data, website_link=form.website_link.data,
                        seeking_talent=form.seeking_talent.data,
                        seeking_description=form.seeking_description.data)
        try:
            # TODO: insert form data as a new Venue record in the db, instead
            db.session.add(newvenu)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!', category="success")
        except:
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' +
                  newvenu.name + ' could not be listed.', category="error")
        finally:
            return render_template('pages/home.html')
    else:
        flash('All fields are required.', category="warning")
        return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('the venue '+venue_id+' has been deleted', category="success")
    except:
        flash('Error while deleting the venue '+venue_id, category="error")
        db.session.rollback()
    finally:
        db.session.close()
        return jsonify({'message': 'delete venue'})


#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []

    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach term
    search_term = request.form.get('search_term', '')
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    artistsquery = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    data = []
    for artist in artistsquery.all():
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": Show.query.filter(
                Show.artist_id == artist.id, Show.start_time >= datetime.today()).count()
        })
    response = {
        "count": artistsquery.count(),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)

    showquery = Show.query.filter(
        Show.artist_id == artist_id, Show.start_time >= datetime.today())

    pastshowquery = Show.query.filter(
        Show.artist_id == artist_id, Show.start_time < datetime.today())
    pastshows = []
    artistShow = []

    for show in showquery.all():
        artistShow.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time)
        })

    for show in pastshowquery.all():
        pastshows.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time)
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres[1:-1].split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": pastshows,
        "upcoming_shows": artistShow,
        "past_shows_count": len(pastshows),
        "upcoming_shows_count": len(artistShow),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    # TODO: populate form with fields from artist with ID <artist_id>
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    updatedArtist = Artist.query.get(artist_id)
    if form.validate_on_submit():
        try:
            # TODO: take values from the form submitted, and update existing
            updatedArtist.name = form.name.data
            updatedArtist.genres = form.genres.data
            updatedArtist.city = form.city.data
            updatedArtist.state = form.state.data
            updatedArtist.phone = form.phone.data
            updatedArtist.website_link = form.website_link.data
            updatedArtist.facebook_link = form.facebook_link.data
            updatedArtist.seeking_venue = form.seeking_venue.data
            updatedArtist.seeking_description = form.seeking_description.data
            updatedArtist.image_link = form.image_link.data
            db.session.commit()
            # on successful db update, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully edited!', category="success")
        except:
            # TODO: on unsuccessful db update, flash an error instead.
            flash('An error occurred. Artist ' +
                  updatedArtist.name + ' could not be edited.', category="error")
            db.session.rollback()
        finally:
            db.session.close()
            return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        flash('All fields are required.', category="warning")
        return render_template('forms/edit_artist.html', form=form, artist=updatedArtist)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.get(venue_id)

    # TODO: populate form with values from venue with ID <venue_id>
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if form.validate_on_submit():
        try:
            # TODO: take values from the form submitted, and update existing
            venue.name = form.name.data
            venue.genres = form.genres.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.address = form.address.data
            venue.website_link = form.website_link.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data
            db.session.commit()
            # on successful db update, flash success
            flash('Venue ' + request.form['name'] +
                  ' was successfully edited!', category="success")
        except:
            # TODO: on unsuccessful db update, flash an error instead.
            flash('An error occurred. Artist ' +
                  venue.name + ' could not be edited.', category="error")
            db.session.rollback()
        finally:
            db.session.close()
            return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash('All fields are required.', category="warning")
        return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    if form.validate_on_submit():
        # TODO: insert form data as a new Artist record in the db, instead
        newArtist = Artist(name=form.name.data,
                           city=form.city.data, state=form.state.data,
                           genres=form.genres.data, phone=form.phone.data, image_link=form.image_link.data,
                           facebook_link=form.facebook_link.data, website_link=form.website_link.data,
                           seeking_venue=form.seeking_venue.data,
                           seeking_description=form.seeking_description.data)
        try:
            db.session.add(newArtist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!', category="success")

        except:
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  newArtist.name + ' could not be listed.', category="error")
            db.session.rollback()
        finally:
            db.session.close()
            return render_template('pages/home.html')
    else:
        flash('All fields are required.', category="warning")
        return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm()
    if form.validate_on_submit():
        # TODO: insert form data as a new Show record in the db, instead
        newShow = Show(artist_id=form.artist_id.data,
                       venue_id=form.venue_id.data, start_time=form.start_time.data)
        try:
            db.session.add(newShow)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!', category="success")
        except:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            flash('An error occurred. Show could not be listed.', category="error")
            db.session.rollback()
        finally:
            db.session.close()
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            return render_template('pages/home.html')

    flash('Make sure you entered all required information.', category="warning")
    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
