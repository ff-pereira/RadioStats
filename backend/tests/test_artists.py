"""
    author: ffpereira
    date: 2025-09-05
"""

from tests.base_test_case import BaseTestCase


class ArtistTests(BaseTestCase):
    def test_get_artists(self):
        rv = self.client.get('/api/artists')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 2
        assert rv.json['data'][0]['artist_type'] == "Solo"
        assert rv.json['data'][1]['artist_type'] == "Band"
        assert rv.json['data'][0]['date_of_birth'] is None
        assert rv.json['data'][0]['nationality'] == "US"
        assert len(rv.json['data'][0]['songs']) == 3
        assert len(rv.json['data'][1]['songs']) == 1

        rv = self.client.get('/api/artists?offset=1&limit=1')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 2
        assert rv.json['pagination']['offset'] == 1
        assert rv.json['pagination']['limit'] == 1
        assert rv.json['data'][0]['name'] == "NAPA"
        assert rv.json['data'][0]['artist_type'] == "Band"

        rv = self.client.get('/api/artists?offset=200&limit=1')
        assert rv.status_code == 400

    def test_get_artist(self):
        rv = self.client.get('/api/artist/26896')
        assert rv.status_code == 200
        assert rv.json['id'] == 26896
        assert rv.json['name'] == "Alex Warren"
        assert rv.json['nationality'] == "US"

        rv = self.client.get('/api/artist/27110')
        assert rv.status_code == 200
        assert rv.json['id'] == 27110
        assert rv.json['name'] == "NAPA"
        assert rv.json['nationality'] is None

        rv = self.client.get('/api/artist/123')
        assert rv.status_code == 404

    def test_get_most_played_artists(self):
        rv = self.client.get('/api/artists/most_played')
        assert rv.status_code == 200
        # print(rv.get_json())
        assert rv.json["data"][0]["count"] == 5
        assert rv.json["data"][0]["id"] == 26896
        assert rv.json["data"][0]["lead"]["songs"] == 3
        assert rv.json["data"][1]["other"]["songs"] == 0
        assert rv.json["data"][1]["count"] == 2
        assert rv.json["data"][1]["id"] == 27110
        assert rv.json["data"][0]["lead"]["songs"] == 3
        assert rv.json["data"][1]["other"]["songs"] == 0
        assert rv.json['pagination']['total'] == 2

        rv = self.client.get('/api/artists/most_played?offset=1&limit=1')
        assert rv.status_code == 200
        assert rv.json["data"][0]["id"] == 27110
        assert rv.json['pagination']['total'] == 2
        assert rv.json['pagination']['offset'] == 1
        assert rv.json['pagination']['limit'] == 1

        rv = self.client.get('/api/artists/most_played?offset=200&limit=2')
        assert rv.status_code == 200
        assert rv.json['pagination']['offset'] == 200
        assert len(rv.json["data"]) == 0

    def test_artist_ranking(self):
        rv = self.client.get('/api/artist/ranking/26896')
        assert rv.status_code == 200
        assert rv.json["percentile"] == 50
        assert rv.json["rank"] == 1

        rv = self.client.get('/api/artist/ranking/27110')
        assert rv.status_code == 200
        assert rv.json["percentile"] == 100
        assert rv.json["rank"] == 2

        rv = self.client.get('/api/artist/ranking/26896?radios=1')
        assert rv.status_code == 200
        assert rv.json["percentile"] == 50
        assert rv.json["rank"] == 1

        rv = self.client.get('/api/artist/ranking/26896?lead=0')
        assert rv.status_code == 404

    def test_top_artists_no_description(self):
        rv = self.client.get('/api/no_description_top')
        assert rv.status_code == 200
        assert len(rv.json) == 1
        assert rv.json[0]["description"] is None
        assert rv.json[0]["artist_id"] == 27110
        assert rv.json[0]["artist_name"] == "NAPA"
        assert rv.json[0]["plays_count"] == 2

    def test_update_artist(self):
        rv = self.client.get('/api/artist/27110')
        assert rv.status_code == 200
        assert rv.json['nationality'] is None
        assert rv.json['description'] is None

        update_data = {"nationality": "PT", "description": "An indie band from Madeira, Portugal."}
        rv = self.client.post('/api/update_artist/27110', json=update_data)
        assert rv.status_code == 200

        rv = self.client.get('/api/artist/27110')
        assert rv.status_code == 200
        assert rv.json['nationality'] == "PT"
        assert rv.json['description'] == "An indie band from Madeira, Portugal."

        rv = self.client.post('/api/update_artist/123', json=update_data)
        assert rv.status_code == 404

    def test_artist_stats(self):
        rv = self.client.get('/api/artist/stats/26896')
        assert rv.status_code == 200
        assert rv.json["avg_plays_per_song"] == 1.67
        assert rv.json["hourly_counts"]["122755"]["21"] == 1
        assert rv.json["most_played"]["month"][0]["value"] == "2025-09"
        assert rv.json["time_of_day_counts"]["dawn"] == 2

        rv = self.client.get('/api/artist/stats/26896?lead=0')
        assert rv.status_code == 200
        assert rv.json["different_songs_count"] == 0
        assert rv.json["daily_counts"] == {}
        assert rv.json["hourly_counts"] == {}

        rv = self.client.get('/api/artist/stats/26896?radios=1')
        assert rv.status_code == 200
        assert rv.json["avg_plays_per_song"] == 1
        assert rv.json["hourly_counts"]["122755"]["0"] == 1
        assert rv.json["most_played"]["month"][0]["value"] == "2025-08"
        assert rv.json["time_of_day_counts"]["afternoon"] == 1

        rv = self.client.get('/api/artist/stats/26896?lead=0&radios=3')
        assert rv.status_code == 200
        assert rv.json["different_songs_count"] == 0
        assert rv.json["daily_counts"] == {}
        assert rv.json["hourly_counts"] == {}

        rv = self.client.get('/api/artist/stats/123')
        assert rv.status_code == 404
