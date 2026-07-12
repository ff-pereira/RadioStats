"""
    author: ffpereira
    date: 2025-09-05
"""

from tests.base_test_case import BaseTestCase


class RadioTests(BaseTestCase):
    def test_get_radios(self):
        rv = self.client.get('/api/radios')
        assert rv.status_code == 200
        assert len(rv.get_json()) == 3
        assert rv.json[0]['id'] == 1
        assert rv.json[0]['name'] == "radio-comercial"
        assert rv.json[1]['id'] == 2
        assert rv.json[1]['name'] == "cidade"
        assert rv.json[2]['id'] == 3
        assert rv.json[2]['name'] == "m80"

    def test_get_radio(self):
        rv = self.client.get('/api/radio/1')
        assert rv.status_code == 200
        assert rv.json['id'] == 1
        assert rv.json['name'] == "radio-comercial"

        rv = self.client.get('/api/radio/2')
        assert rv.status_code == 200
        assert rv.json['id'] == 2
        assert rv.json['name'] == "cidade"

        rv = self.client.get('/api/radio/123')
        assert rv.status_code == 404

    def test_artist_radios(self):
        rv = self.client.get('/api/radios/artist/26896')
        assert rv.status_code == 200
        assert len(rv.json["radio_names"]) == 3

        rv = self.client.get('/api/radios/artist/27110')
        assert rv.status_code == 200
        assert len(rv.json["radio_names"]) == 2

        rv = self.client.get('/api/radios/artist/27110?lead=0')
        assert rv.status_code == 200
        assert len(rv.json["radio_names"]) == 0

        rv = self.client.get('/api/radios/artist/123?lead=3')
        assert rv.status_code == 400

        rv = self.client.get('/api/radios/artist/123')
        assert rv.status_code == 404

    def test_song_radios(self):
        rv = self.client.get('/api/radios/song/122755')
        assert rv.status_code == 200
        assert len(rv.json["radio_names"]) == 2

        rv = self.client.get('/api/radios/song/123016')
        assert rv.status_code == 200
        assert len(rv.json["radio_names"]) == 1

        rv = self.client.get('/api/radios/song/122987')
        assert rv.status_code == 200
        assert len(rv.json["radio_names"]) == 2

        rv = self.client.get('/api/radios/song/123')
        assert rv.status_code == 404

    def test_radio_stats(self):
        rv = self.client.get('/api/radio/stats/1')
        assert rv.status_code == 200
        assert rv.json["avg_plays_per_song"] == 1
        assert rv.json["different_songs_count"] == 4
        assert rv.json["first_day"] == "2025-07-28"
        assert rv.json["most_played"]["month"][0]["value"] == "2025-08"
        assert rv.json["time_of_day_counts"]["dawn"] == 3
        assert rv.json["name"] == "radio-comercial"
