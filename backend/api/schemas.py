"""
    author: ffpereira
    date: 2025-09-05
"""

from api import ma, db
from api.models import Radio, Song, Play, Album, Artist, OtherArtist, NoMcr

from marshmallow import validates, validates_schema, ValidationError, fields

paginated_schema_cache = {}


class EmptySchema(ma.Schema):
    pass


class DateTimePaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.DateTime(load_only=True)
    before = ma.DateTime(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)


class StringPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.String(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')


class MostPlayedPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    offset = ma.Integer()
    radios = ma.String()
    after = ma.String()
    before = ma.String()
    limit = ma.Integer()
    song_search = ma.String()
    artist_search = ma.String()


class StatsPaginationSchema(ma.Schema):
    radios = ma.String()


class ArtistStatsArgsSchema(ma.Schema):
    lead = ma.Boolean()
    radios = ma.String()


class PlayStatsArgsSchema(ma.Schema):
    radios = ma.String()
    after = ma.String()
    before = ma.String()
    song_search = ma.String()
    artist_search = ma.String()


def PaginatedCollection(schema, pagination_schema=StringPaginationSchema):
    if schema in paginated_schema_cache:
        return paginated_schema_cache[schema]

    class PaginatedSchema(ma.Schema):
        class Meta:
            ordered = True

        pagination = ma.Nested(pagination_schema)
        data = ma.Nested(schema, many=True)

    PaginatedSchema.__name__ = 'Paginated{}'.format(schema.__class__.__name__)
    paginated_schema_cache[schema] = PaginatedSchema
    return PaginatedSchema


class RadioSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Radio
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
    name = ma.String(required=True)
    country = ma.String(required=True)
    logo = ma.String(dump_only=True)


class OtherArtistSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OtherArtist
        ordered = True

    id = ma.Integer(dump_only=True, attribute="artist_id")
    name = ma.String(dump_only=True, attribute="name")


class SongSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Song
        ordered = True

    id = ma.auto_field(required=True)
    url = ma.String(dump_only=True)
    name = ma.String(required=True)
    lead_artist_id = ma.Integer(required=True)
    lead_artist_name = ma.String(dump_only=True, attribute="lead_artist.name")
    album_id = ma.Integer(required=False)
    album_cover_url = ma.String(dump_only=True)
    sample = ma.String(dump_only=True, attribute="sample_url")
    total_plays = ma.Integer(dump_only=True)
    other_artists = ma.Nested(OtherArtistSchema, many=True, dump_only=True, attribute="other_artists")

    @validates('id')
    def validate_id(self, value):
        if value <= 0:
            raise ValidationError('ID must be a positive integer')
        if db.session.get(Song, value):
            raise ValidationError('ID must be unique')

    @validates('lead_artist_id')
    def validate_lead_artist_id(self, value):
        if not db.session.get(Artist, value):
            raise ValidationError('Artist does not exist')

    @validates('album_id')
    def validate_album_id(self, value):
        if not db.session.get(Album, value):
            raise ValidationError('Album does not exist')


class AlbumSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Album
        ordered = True

    id = ma.auto_field(required=True)
    url = ma.String(dump_only=True)
    artist_id = ma.Integer(required=True)
    artist_name = ma.String(dump_only=True, attribute="artist.name")
    name = ma.String(required=True)
    type = ma.String(required=True)
    songs = ma.Nested(SongSchema, many=True, dump_only=True)

    @validates('id')
    def validate_id(self, value):
        if value <= 0:
            raise ValidationError('ID must be a positive integer')
        if db.session.get(Album, value):
            raise ValidationError('ID must be unique')

    @validates('artist_id')
    def validate_artist_id(self, value):
        if not db.session.get(Artist, value):
            raise ValidationError('Artist does not exist')


class ArtistSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Artist
        ordered = True

    id = ma.auto_field(required=True)
    url = ma.String(dump_only=True)
    name = ma.String(required=True)
    description = ma.String(required=False, allow_none=True)
    nationality = ma.String(required=False,allow_none=True)
    date_of_birth = ma.DateTime(required=False, allow_none=True)
    date_of_death = ma.DateTime(required=False, allow_none=True)
    artist_type = ma.String(required=False, allow_none=True)
    flag = ma.String(dump_only=True)

    songs = ma.Nested(SongSchema, many=True, dump_only=True)
    # songs_as_other = ma.Nested(OtherArtistSchema, many=True, dump_only=True)
    songs_as_other = ma.Nested(SongSchema, many=True, dump_only=True)

    @validates('id')
    def validate_id(self, value):
        if value <= 0:
            raise ValidationError('ID must be a positive integer')
        if db.session.get(Artist, value):
            raise ValidationError('ID must be unique')

class PlaySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Play
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
    radio_id = ma.Integer(required=True)
    song_id = ma.Integer(required=True)
    song_name = ma.String(dump_only=True, attribute="song.name")
    artist_id = ma.Integer(dump_only=True, attribute="song.lead_artist.id")
    artist_name = ma.String(dump_only=True, attribute="song.lead_artist.name")
    album_id = ma.Integer(dump_only=True, attribute="song.album_id")
    timestamp = ma.DateTime(required=True)
    album_cover_url = ma.String(dump_only=True)
    sample = ma.String(dump_only=True)

    @validates('radio_id')
    def validate_radio_id(self, value):
        if not db.session.get(Radio, value):
            raise ValidationError('Radio does not exist')

    @validates('song_id')
    def validate_song_id(self, value):
        if not db.session.get(Song, value):
            raise ValidationError('Song does not exist')


class NoMcrSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoMcr
        ordered = True

    id = ma.auto_field(dump_only=True)
    url = ma.String(dump_only=True)
    radio_id = ma.Integer(required=True)
    timestamp = ma.DateTime(required=True)
    song_name = ma.String(required=True)
    artist_name = ma.String(required=True)
    item_code = ma.String(required=True)

    @validates('radio_id')
    def validate_radio_id(self, value):
        if not db.session.get(Radio, value):
            raise ValidationError('Radio does not exist')


class MostPlayedSongSchema(ma.Schema):
    id = fields.Integer()
    song_name = fields.String()
    play_count = fields.Integer()
    album_id = fields.Integer()
    artist_id = fields.Integer()
    artist_name = fields.String()
    album_cover_url = fields.String(allow_none=True)
    sample = fields.String(allow_none=True)
    avg_per_day = fields.Float()


class MostPlayedArtistSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    count = fields.Integer()
    total_songs = fields.Integer()
    lead = fields.Nested({
        'play_count': fields.Integer(),
        'songs': fields.Integer(),
        'albums': fields.Integer(),
        #'avg_per_day': fields.Float()
    })
    other = fields.Nested({
        'play_count': fields.Integer(),
        'songs': fields.Integer(),
        'albums': fields.Integer(),
        #'avg_per_day': fields.Float()
    })
    avg_per_day = fields.Float()
    different_songs = fields.Integer()


class ArtistStatsResponseSchema(ma.Schema):
    artist_id = fields.Int(required=True)
    total_plays = fields.Int(required=True)
    daily_counts = fields.Dict(
        keys=fields.String(),
        values=fields.Dict(
            keys=fields.String(),
            values=fields.Raw()
        ),
        required=True
    )
    play_counts_by_song = fields.List(fields.Dict(keys=fields.String(), values=fields.Raw()), required=True)
    different_songs_count = fields.Int(required=True)
    avg_plays_per_song = fields.Float(required=True)
    song_names = fields.Dict(keys=fields.Raw(), values=fields.String(), required=True)
    most_played = fields.Dict(
        keys=fields.String(),
        values=fields.List(
            fields.Dict(keys=fields.String(), values=fields.Raw())
        ),required=True
    )
    time_of_day_counts = fields.Dict( keys=fields.String(), values=fields.Raw(), required=True)
    weekday_counts = fields.Dict( keys=fields.String(), values=fields.Raw(), required=True)
    hourly_counts = fields.Dict( keys=fields.String(), values=fields.Raw(), required=True)


class SongStatsResponseSchema(ma.Schema):
    song_id = fields.Int(required=True)
    daily_counts = fields.Dict(keys=fields.String(), values=fields.Dict(keys=fields.String(), values=fields.Raw()), required=True)
    total_plays = fields.Int(required=True)
    radio_names = fields.Dict(keys=fields.Raw(), values=fields.String(), required=True)
    play_counts_by_radio = fields.List(fields.Dict(keys=fields.String(), values=fields.Raw()), required=True)
    different_radios_count = fields.Int(required=True)
    most_played = fields.Raw(required=True)
    time_of_day_counts = fields.Dict(keys=fields.String(), values=fields.Raw(), required=True)
    weekday_counts = fields.Dict(keys=fields.String(), values=fields.Raw(), required=True)
    hourly_counts = fields.Dict(keys=fields.String(), values=fields.Raw(), required=True)


class RadioNamesSchema(ma.Schema):
    radio_names = fields.Dict(
        keys=fields.Integer(),
        values=fields.String()
    )