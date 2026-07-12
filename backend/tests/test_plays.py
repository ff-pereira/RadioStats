"""
    author: ffpereira
    date: 2025-09-05
"""

from email.utils import parsedate_to_datetime
from tests.base_test_case import BaseTestCase


class PlayTests(BaseTestCase):

    def test_get_plays(self):
        rv = self.client.get('/api/plays')
        assert rv.status_code == 200
        assert rv.json['pagination']['count'] == 7
        assert rv.json['pagination']['total'] == 7
        assert rv.json['data'][0]['radio_id'] == 1
        assert rv.json['data'][0]['artist_name'] == "Alex Warren"
        assert rv.json['data'][1]['radio_id'] == 2
        assert rv.json['data'][1]['song_id'] == 122755
        assert rv.json['data'][5]['song_id'] == 122714
        assert rv.json['data'][6]['artist_name'] == "NAPA"

        rv = self.client.get('/api/plays?limit=2025')
        assert rv.status_code == 200
        assert rv.json['pagination']['limit'] == 25

        rv = self.client.get('/api/plays?after=2025-09-01T12:05:54')
        assert rv.status_code == 200
        assert rv.json['pagination']['count'] == 2
        assert rv.json['pagination']['offset'] == 5
        assert rv.json['data'][0]['artist_name'] == "NAPA"
        assert rv.json['data'][1]['radio_id'] == 1
        assert rv.json['data'][1]['song_id'] == 122714

        rv = self.client.get('/api/plays?before=2025-09-01T12:05:54')
        assert rv.status_code == 200
        assert rv.json['pagination']['count'] == 4
        assert rv.json['pagination']['offset'] == 3
        assert rv.json['data'][0]['radio_id'] == 1
        assert rv.json['data'][0]['artist_name'] == "Alex Warren"
        assert rv.json['data'][2]['artist_id'] == 27110
        assert rv.json['data'][2]['song_id'] == 122714

    def test_get_play(self):
        rv = self.client.get('/api/plays/1')
        assert rv.status_code == 200
        assert rv.json['id'] == 1
        assert rv.json['radio_id'] == 1
        assert rv.json['artist_name'] == "Alex Warren"

        rv = self.client.get('/api/plays/5')
        assert rv.status_code == 200
        assert rv.json['id'] == 5
        assert rv.json['radio_id'] == 1
        assert rv.json['song_id'] == 122987

        rv = self.client.get('/api/plays/123')
        assert rv.status_code == 404

    def test_interval(self):
        rv = self.client.get('/api/interval')
        assert rv.status_code == 200
        assert "first_play" in rv.json
        assert "last_play" in rv.json
        first = parsedate_to_datetime(rv.json["first_play"])
        last = parsedate_to_datetime(rv.json["last_play"])
        assert first < last

    def test_play_stats(self):
        rv = self.client.get('/api/stats')
        assert rv.status_code == 200
        assert rv.json['total_plays'] == 7
        assert rv.json['total_different_songs'] == 4

        rv = self.client.get('/api/stats?radios=1,2&song_search=des&artist_search=napa')
        assert rv.status_code == 200
        assert rv.json['total_plays'] == 2
        assert rv.json['total_different_songs'] == 1

        rv = self.client.get('/api/stats?after=2025-09-01T12:00:00&before=2025-09-01T13:00:00')
        assert rv.status_code == 200
        assert rv.json['total_plays'] == 1
        assert rv.json['total_different_songs'] == 1
