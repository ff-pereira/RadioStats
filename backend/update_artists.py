"""
    author: ffpereira
    date: 2025-11-12
"""

import os

from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, desc

from api.models import Song, Play, Artist

from gemini_api import ask_gemini

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
ALCHEMICAL_DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_engine(ALCHEMICAL_DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

artists = (
    db.query(
        Artist.id,
        Artist.name,
        Artist.nationality,
        Artist.description,
        func.count(Play.id).label('plays_count'),
        func.string_agg(func.distinct(Song.name), ', ').label('song_names'),
    )
    .join(Song, Song.lead_artist_id == Artist.id)
    .join(Play, Play.song_id == Song.id)
    .filter(Artist.description.is_(None) | (Artist.nationality.is_(None)))
    .group_by(Artist.id, Artist.name)
    .order_by(desc('plays_count'))
    .limit(100)
    .all()
)

updated_count = 1
for artist in artists:
    now = datetime.now()
    print(f"{now} - {updated_count}/10 - {artist.id} - {artist.name}; Plays: {artist.plays_count}, Songs: {artist.song_names}")

    artist_info = ask_gemini(artist.name, artist.song_names, 5)
    print(artist_info)

    existing_artist = db.get(Artist, artist.id)
    if existing_artist:
        if artist_info.get("description"):
            existing_artist.description = artist_info["description"]
        if artist_info.get("nationality"):
            existing_artist.nationality = artist_info["nationality"]
        if artist_info.get("date_of_birth"):
            existing_artist.date_of_birth = artist_info["date_of_birth"]
        if artist_info.get("date_of_death"):
            existing_artist.date_of_death = artist_info["date_of_death"]
        if artist_info.get("artist_type"):
            existing_artist.artist_type = artist_info["artist_type"]

        updated_count += 1
        db.commit()

    db.commit()
