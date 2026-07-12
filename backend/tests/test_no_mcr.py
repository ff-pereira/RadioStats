"""
    author: ffpereira
    date: 2025-09-05
"""

from tests.base_test_case import BaseTestCase


class NoMcrTests(BaseTestCase):

    def test_get_no_mcrs(self):
        rv = self.client.get('/api/no_mcrs')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 3
        assert rv.json['data'][0]['artist_name'] == "Unknown Artist"
        assert rv.json['data'][0]['radio_id'] == 2
        assert rv.json['data'][1]['song_name'] == "No Signal"
        assert rv.json['data'][1]['radio_id'] == 3

        rv = self.client.get('/api/no_mcrs?limit=2025')
        assert rv.status_code == 200
        assert rv.json['pagination']['limit'] == 25

        rv = self.client.get('/api/no_mcrs?before=2025-08-05T10:00:00&after=2025-08-19T10:00:00')
        assert rv.status_code == 400

        rv = self.client.get('/api/no_mcrs?after=2025-08-19T10:00:00&offset=12')
        assert rv.status_code == 400

        rv = self.client.get('/api/no_mcrs?after=2025-08-19T10:00:00&before=2025-08-19')
        assert rv.status_code == 400

    def test_get_no_mcr(self):
        rv = self.client.get('/api/no_mcrs/1')
        assert rv.status_code == 200
        assert rv.json['id'] == 1
        assert rv.json['song_name'] == "Silent Track"
        assert rv.json['artist_name'] == "Unknown Artist"

        rv = self.client.get('/api/no_mcrs/2')
        assert rv.status_code == 200
        assert rv.json['id'] == 2
        assert rv.json['song_name'] == "No Signal"
        assert rv.json['artist_name'] == "No One"

        rv = self.client.get('/api/no_mcrs/123')
        assert rv.status_code == 404

    def test_top_no_mcr(self):
        rv = self.client.get('/api/no_mcr_top')
        assert rv.status_code == 200
        assert len(rv.json) == 2
        assert rv.json[0]['item_code'] == "IT000002"
        assert rv.json[0]['song_name'] == "No Signal"
        assert rv.json[0]['artist_name'] == "No One"
        assert rv.json[0]['plays_count'] == 2
        assert rv.json[1]['item_code'] == "IT000001"
        assert rv.json[1]['song_name'] == "Silent Track"
        assert rv.json[1]['artist_name'] == "Unknown Artist"
        assert rv.json[1]['plays_count'] == 1

    def test_no_mcr_to_play_api(self):
        """
        Test converting NoMcr entries to Play entries via API request.
        """
        rv = self.client.get('/api/no_mcrs')
        assert rv.status_code == 200
        assert rv.json['pagination']['total'] == 3
        no_mcrs_before = [mcr for mcr in rv.json['data'] if mcr['item_code'] == "IT000002"]
        assert len(no_mcrs_before) == 2

        rv = self.client.post('/api/no_mcr_to_play/IT000002/123500')
        assert rv.status_code == 200

        rv = self.client.get('/api/no_mcrs')
        assert rv.json['pagination']['total'] == 1
        assert rv.status_code == 200
        no_mcrs_after = [mcr for mcr in rv.json['data'] if mcr['item_code'] == "IT000002"]
        assert len(no_mcrs_after) == 0
