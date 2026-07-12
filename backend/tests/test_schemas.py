"""
    author: ffpereira
    date: 2025-09-05
"""
import pytest
from marshmallow import ValidationError

from api import ma
from api.schemas import PaginatedCollection, StringPaginationSchema, SongSchema, AlbumSchema, ArtistSchema, PlaySchema, NoMcrSchema

from tests.base_test_case import BaseTestCase


class SchemaTests(BaseTestCase):

    def test_paginated_collection_caches_schema(self):
        class MySchema(ma.Schema):
            field = ma.String()

        first = PaginatedCollection(MySchema)
        second = PaginatedCollection(MySchema)

        assert first is second

        schema_instance = first()
        assert 'data' in schema_instance.fields
        assert 'pagination' in schema_instance.fields

    def test_string_pagination_schema(selft):
        schema = StringPaginationSchema()

        # Case 1: Both offset and after specified → should raise ValidationError
        with pytest.raises(ValidationError) as exc:
            schema.load({"limit": 10, "offset": 5, "after": "abc123"})
        assert "Cannot specify both offset and after" in str(exc.value)

    def test_song_schema(self):
        schema = SongSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": -1, "name": "Song", "lead_artist_id": 26896})
        assert "ID must be a positive integer" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": 122755, "name": "Song", "lead_artist_id": 26896})
        assert "ID must be unique" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": 2, "name": "Song", "lead_artist_id": 999})
        assert "Artist does not exist" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": 3, "name": "Song", "lead_artist_id": 26896, "album_id": 123})
        assert "Album does not exist" in str(exc.value)

    def test_album_schema(self):
        schema = AlbumSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": -1, "name": "Album", "type": "single", "artist_id": 26896})
        assert "ID must be a positive integer" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": 55501, "name": "Album", "type": "single", "artist_id": 26896})
        assert "ID must be unique" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": 2, "name": "Album", "type": "single", "artist_id": 999})
        assert "Artist does not exist" in str(exc.value)

    def test_artist_schema(self):
        schema = ArtistSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": -1, "name": "Artist"})
        assert "ID must be a positive integer" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            schema.load({"id": 26896, "name": "Artist"})
        assert "ID must be unique" in str(exc.value)

    def test_play_schema(self):
        schema = PlaySchema()

        with pytest.raises(ValidationError) as exc:
            schema.load({"radio_id": 999, "song_id": 122755, "timestamp": "2025-08-31T00:00:34"})
        assert "Radio does not exist" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            schema.load({"radio_id": 1, "song_id": 999999, "timestamp": "2025-08-31T00:00:34"})
        assert "Song does not exist" in str(exc.value)

    def test_no_mcr_schema(self):
        schema = NoMcrSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load({"item_code": "IT000001", "radio_id": 123, "song_name": "Song", "timestamp": "2025-08-31T00:00:34"})
        assert "Radio does not exist" in str(exc.value)
