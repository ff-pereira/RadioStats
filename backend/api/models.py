"""
    author: ffpereira
    date: 2025-09-05
"""

import sqlalchemy as sa
from flask import url_for
from alchemical import Model
from sqlalchemy import orm as so
from datetime import datetime, date


class Radio(Model):
    __tablename__ = 'radios'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    country: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)

    plays: so.Mapped[list["Play"]] = so.relationship("Play", back_populates="radio")

    @property
    def url(self):
        return url_for('radios.get_radio', radio_id=self.id)

    @property
    def logo(self):
        return url_for('static', filename=f"images/radios/{self.id}.jpg", _external=True)


class Artist(Model):
    __tablename__ = 'artists'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    nationality: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, nullable=True)
    date_of_birth: so.Mapped[date] = so.mapped_column(sa.Date, index=True, nullable=True)
    date_of_death: so.Mapped[date] = so.mapped_column(sa.Date, index=True, nullable=True)
    artist_type: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, nullable=True)

    songs: so.Mapped[list["Song"]] = so.relationship("Song", back_populates="lead_artist")
    albums: so.Mapped[list["Album"]] = so.relationship("Album", back_populates="artist")

    songs_as_other: so.Mapped[list["Song"]] = so.relationship(
        "Song",
        secondary="other_artists",
        primaryjoin="Artist.id==OtherArtist.artist_id",
        secondaryjoin="Song.id==OtherArtist.song_id",
        viewonly=True
    )

    @property
    def url(self):
        return url_for('artists.get_artist', artist_id=self.id)

    @property
    def flag(self):
        if self.nationality:
            return url_for('static', filename=f"flags/w160/{self.nationality.lower()}.png", _external=True)
        return None


class OtherArtist(Model):
    __tablename__ = 'other_artists'

    song_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('songs.id'), primary_key=True)
    artist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('artists.id'), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)

    song: so.Mapped["Song"] = so.relationship("Song", backref="other_artists")


class Album(Model):
    __tablename__ = 'albums'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    artist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('artists.id'), index=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, nullable=True)
    type: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)

    artist: so.Mapped["Artist"] = so.relationship("Artist", back_populates="albums")
    songs: so.Mapped[list["Song"]] = so.relationship("Song", backref="album")


class Song(Model):
    __tablename__ = 'songs'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    item_code: so.Mapped[str] = so.mapped_column(sa.Text, index=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    lead_artist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('artists.id'), index=True)
    album_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('albums.id'), index=True, nullable=True)
    sample: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=False)

    lead_artist: so.Mapped["Artist"] = so.relationship("Artist", back_populates="songs")
    plays: so.Mapped[list["Play"]] = so.relationship("Play", back_populates="song")

    @property
    def url(self):
        return url_for('songs.get_song', song_id=self.id)

    @property
    def album_cover_url(self):
        if self.album_id:
            return url_for('static', filename=f"images/albums/{self.album_id}.jpg", _external=True)
        return None

    @property
    def sample_url(self):
        return url_for('static', filename=f"samples/{self.id}.mp4", _external=True)


class NoMcr(Model):
    __tablename__ = 'no_mcr'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    item_code: so.Mapped[str] = so.mapped_column(sa.Text, index=True)
    radio_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('radios.id'), index=True)
    song_name: so.Mapped[str] = so.mapped_column(sa.Text, index=True)
    artist_name: so.Mapped[str] = so.mapped_column(sa.Text, index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True)

    @property
    def url(self):
        return url_for('no_mcrs.get_no_mcr', no_mcr_id=self.id)


class Play(Model):
    __tablename__ = 'plays'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    radio_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('radios.id'), index=True)
    song_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('songs.id'), index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True)

    radio: so.Mapped["Radio"] = so.relationship("Radio", back_populates="plays")
    song: so.Mapped["Song"] = so.relationship("Song", back_populates="plays")

    @property
    def url(self):
        return url_for('plays.get_play', play_id=self.id)

    @property
    def album_cover_url(self):
        return url_for('static', filename=f"images/albums/{self.song.album_id}.jpg", _external=True)

    @property
    def sample(self):
        return url_for('static', filename=f"samples/{self.song_id}.mp4", _external=True)
