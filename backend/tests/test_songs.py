"""
    author: ffpereira
    date: 2025-09-05
"""

from tests.base_test_case import BaseTestCase


class SongTests(BaseTestCase):

    def test_get_songs(self):
        rv = self.client.get('/api/songs')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 5
        assert rv.json['data'][0]['id'] == 122714
        assert rv.json['data'][0]['lead_artist_id'] == 27110
        assert rv.json['data'][0]['lead_artist_name'] == "NAPA"
        assert rv.json['data'][0]['name'] == "Deslocado"
        assert len(rv.json['data'][0]['other_artists']) == 0
        assert rv.json['data'][2]['id'] == 122987
        assert rv.json['data'][2]['lead_artist_id'] == 26896
        assert rv.json['data'][2]['lead_artist_name'] == "Alex Warren"
        assert rv.json['data'][2]['name'] == "On My Mind"
        assert len(rv.json['data'][2]['other_artists']) == 0

        rv = self.client.get('/api/songs?offset=2&limit=2')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 5
        assert rv.json['pagination']['offset'] == 2
        assert rv.json['data'][0]['id'] == 122987
        assert rv.json['data'][0]['lead_artist_id'] == 26896
        assert rv.json['data'][0]['lead_artist_name'] == "Alex Warren"
        assert rv.json['data'][0]['name'] == "On My Mind"
        assert len(rv.json['data'][0]['other_artists']) == 0

        rv = self.client.get('/api/songs?offset=200&limit=2')
        assert rv.status_code == 400

    def test_get_song(self):
        rv = self.client.get('/api/song/122755')
        assert rv.status_code == 200
        assert rv.json['id'] == 122755
        assert rv.json['name'] == "Ordinary"
        assert rv.json['lead_artist_id'] == 26896
        assert rv.json['lead_artist_name'] == "Alex Warren"
        assert len(rv.json['other_artists']) == 0

        rv = self.client.get('/api/song/122714')
        assert rv.status_code == 200
        assert rv.json['id'] == 122714
        assert rv.json['name'] == "Deslocado"
        assert rv.json['lead_artist_id'] == 27110
        assert rv.json['lead_artist_name'] == "NAPA"
        assert len(rv.json['other_artists']) == 0

        rv = self.client.get('/api/song/123')
        assert rv.status_code == 404

    def test_get_most_played_songs(self):
        rv = self.client.get('/api/songs/most_played')
        assert rv.status_code == 200
        assert rv.json["data"][0]["play_count"] == 2
        assert rv.json["data"][0]["id"] == 122714
        assert rv.json["data"][0]["artist_id"] == 27110
        assert rv.json["data"][1]["play_count"] == 2
        assert rv.json["data"][1]["id"] == 122755
        assert rv.json["data"][1]["artist_id"] == 26896
        assert rv.json["data"][2]["play_count"] == 2
        assert rv.json["data"][2]["id"] == 122987
        assert rv.json["data"][2]["artist_id"] == 26896
        assert rv.json["data"][3]["play_count"] == 1
        assert rv.json["data"][3]["id"] == 123016
        assert rv.json["data"][3]["artist_id"] == 26896
        assert rv.json['pagination']['total'] == 4

        rv = self.client.get('/api/songs/most_played?offset=1&limit=2')
        assert rv.status_code == 200
        assert rv.json["data"][0]["id"] == 122755
        assert rv.json["data"][1]["id"] == 122987
        assert rv.json['pagination']['total'] == 4
        assert rv.json['pagination']['offset'] == 1
        assert rv.json['pagination']['limit'] == 2

        rv = self.client.get('/api/songs/most_played?radios=1,2&after=2025-08-01')
        assert rv.status_code == 200
        assert rv.json["data"][0]["id"] == 122755
        assert rv.json["data"][1]["id"] == 122987
        assert rv.json['pagination']['total'] == 3
        assert rv.json['pagination']['offset'] == 0

        rv = self.client.get('/api/songs/most_played?radios=1,2&before=2026-08-01')
        assert rv.status_code == 200
        assert rv.json["data"][0]["id"] == 122714
        assert rv.json["data"][1]["id"] == 122755
        assert rv.json['pagination']['total'] == 4
        assert rv.json['pagination']['offset'] == 0

        rv = self.client.get('/api/songs/most_played?after=2')
        assert rv.status_code == 400

        rv = self.client.get('/api/songs/most_played?before=2025-08-05&after=2025-08-19')
        assert rv.status_code == 400

        rv = self.client.get('/api/songs/most_played?offset=200&limit=2')
        assert rv.status_code == 200
        assert rv.json['pagination']['offset'] == 200
        assert len(rv.json["data"]) == 0

    def test_song_ranking(self):
        rv = self.client.get('/api/song/ranking/122714')
        assert rv.status_code == 200
        assert rv.json['rank'] == 1
        assert rv.json['percentile'] == 25

        rv = self.client.get('/api/song/ranking/123016')
        assert rv.status_code == 200
        assert rv.json['rank'] == 4
        assert rv.json['percentile'] == 100

        rv = self.client.get('/api/song/ranking/123016?radios=1')
        assert rv.status_code == 200
        assert rv.json['rank'] == 1
        assert rv.json['percentile'] == 25

        rv = self.client.get('/api/song/ranking/123')
        assert rv.status_code == 404

    def test_song_stats(self):
        rv = self.client.get('/api/song/stats/122714')
        assert rv.status_code == 200
        assert rv.json["different_radios_count"] == 2
        assert rv.json["hourly_counts"]["2"]["2"] == 1
        assert rv.json["most_played"]["month"][0]["value"] == "2025-07"
        assert rv.json["time_of_day_counts"]["dawn"] == 2

        rv = self.client.get('/api/song/stats/122714?radios=1')
        assert rv.status_code == 200
        assert rv.json["different_radios_count"] == 1
        assert rv.json["hourly_counts"]["1"]["1"] == 1
        assert rv.json["most_played"]["day"][0]["value"] == "2025-07-28"
        assert rv.json["time_of_day_counts"]["dawn"] == 1

        rv = self.client.get('/api/song/stats/123')
        assert rv.status_code == 404
