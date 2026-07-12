"""
    author: ffpereira
    date: 2025-09-05
"""

import unittest
from datetime import datetime

from config import Config

from api.app import create_app, db
from api.models import Radio, Artist, Song, Play, NoMcr, Album


class TestConfig(Config):
    TESTING = True
    ALCHEMICAL_DATABASE_URL = 'sqlite://'


class BaseTestCase(unittest.TestCase):
    config = TestConfig

    def setUp(self):
        self.app = create_app(self.config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self._create_test_data()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.app_context.pop()

    def _create_test_data(self):
        # Radios
        radios_data = [
            {"id": 1, "name": "radio-comercial", "country": "pt"},
            {"id": 2, "name": "cidade", "country": "pt"},
            {"id": 3, "name": "m80", "country": "pt"},
        ]
        radios = [Radio(**data) for data in radios_data]
        db.session.add_all(radios)

        # Artists
        artists_data = [
            {
                "id": 26896,
                "name": "Alex Warren",
                "description": "Alex Warren is an American singer-songwriter and social media personality, known for his presence on platforms like TikTok and YouTube. He gained popularity through his relatable content and music.",
                "nationality": "US",
                "date_of_birth": None,
                "date_of_death": None,
                "artist_type": "Solo",
            },
            {
                "id": 27110,
                "name": "NAPA",
                "description": None,
                "nationality": None,
                "date_of_birth": None,
                "date_of_death": None,
                "artist_type": "Band",
            },
        ]
        artists = [Artist(**data) for data in artists_data]
        db.session.add_all(artists)

        # Albums
        albums_data = [
            {"id": 55501, "type": "single", "name": "Ordinary - Single", "artist_id": 26896},
            {"id": 55502, "type": "single", "name": "Eternity - Single", "artist_id": 26896},
            {"id": 55503, "type": "single", "name": "On My Mind - Single", "artist_id": 26896},
            {"id": 55600, "type": "album", "name": "Deslocado", "artist_id": 27110},
        ]
        albums = [db.session.merge(Album(**data)) for data in albums_data]
        db.session.add_all(albums)

        # Songs
        songs_data = [
            {"id": 122755, "item_code": "IT122755", "name": "Ordinary", "lead_artist_id": 26896, "album_id": 55501},
            {"id": 123016, "item_code": "IT123016", "name": "Eternity", "lead_artist_id": 26896, "album_id": 55502},
            {"id": 122987, "item_code": "IT122987", "name": "On My Mind", "lead_artist_id": 26896, "album_id": 55503},
            {"id": 122714, "item_code": "IT122714", "name": "Deslocado", "lead_artist_id": 27110, "album_id": 55600},
            {"id": 123500, "item_code": "IT000002", "name": "No Signal", "lead_artist_id": 27041}
        ]
        songs = [Song(**data, sample=False) for data in songs_data]
        db.session.add_all(songs)

        # Plays
        plays_data = [
            {"radio_id": 1, "song_id": 122755, "timestamp": "2025-08-31 00:00:34"},
            {"radio_id": 2, "song_id": 122755, "timestamp": "2025-09-01 21:45:57"},
            {"radio_id": 3, "song_id": 122987, "timestamp": "2025-09-02 06:15:33"},
            {"radio_id": 1, "song_id": 123016, "timestamp": "2025-09-01 12:05:54"},
            {"radio_id": 1, "song_id": 122987, "timestamp": "2025-08-30 01:41:28"},
            {"radio_id": 2, "song_id": 122714, "timestamp": "2025-07-28 02:00:13"},
            {"radio_id": 1, "song_id": 122714, "timestamp": "2025-07-28 01:51:02"},
        ]
        plays = [
            Play(
                radio_id=data["radio_id"],
                song_id=data["song_id"],
                timestamp=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
            )
            for data in plays_data
        ]
        db.session.add_all(plays)

        no_mcr_data = [
            {
                "item_code": "IT000001",
                "radio_id": 2,
                "song_name": "Silent Track",
                "artist_name": "Unknown Artist",
                "timestamp": "2025-09-03 10:00:00",
            },
            {
                "item_code": "IT000002",
                "radio_id": 3,
                "song_name": "No Signal",
                "artist_name": "No One",
                "timestamp": "2025-09-04 11:30:00",
            },
            {
                "item_code": "IT000002",
                "radio_id": 3,
                "song_name": "No Signal",
                "artist_name": "No One",
                "timestamp": "2025-09-04 12:30:00",
            },
        ]
        no_mcrs = [
            NoMcr(
                item_code=data["item_code"],
                radio_id=data["radio_id"],
                song_name=data["song_name"],
                artist_name=data["artist_name"],
                timestamp=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
            )
            for data in no_mcr_data
        ]
        db.session.add_all(no_mcrs)

        db.session.commit()
