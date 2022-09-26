from datetime import datetime
from enum import unique
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    db.app = app
    db.init_app(app)


class Show(db.Model):
    __tablename__ = "Show"
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)

    @staticmethod
    def searchShows(ending_date, starting_date):
        showsquery = db.session.query(Show).filter(
            Show.start_time >= starting_date, Show.start_time <= ending_date).order_by(Show.start_time)
        return showsquery

    def __repr__(self) -> str:
        return f'<Show artist: {self.artist_id} venue: {self.venue_id} >'


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    # artists : relationship mamyTomany with artist through show
    shows = db.relationship('Show', backref='venue', lazy=True)

    def past_shows(self):
        past_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venue_id == self.id, Show.start_time < datetime.now())
        return past_shows_query

    def upcoming_shows(self):
        coming_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venue_id == self.id, Show.start_time >= datetime.now())
        return coming_shows_query

    def __repr__(self) -> str:
        return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city} >'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), db.CheckConstraint(
        "phone ~* '((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))'"), unique=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    # venues : relationship mamyTomany with venue through show
    shows = db.relationship('Show', backref='artist', lazy=True)

    def past_shows(self):
        past_shows_query = db.session.query(Show).join(Artist).filter(
            Show.artist_id == self.id, Show.start_time < datetime.now())
        return past_shows_query

    def upcoming_shows(self):
        coming_shows_query = db.session.query(Show).join(Artist).filter(
            Show.artist_id == self.id, Show.start_time >= datetime.now())
        return coming_shows_query

    def __repr__(self) -> str:
        return f'<Artist id: {self.id} name: {self.name} >'
