"""
    author: ffpereira
    date: 2025-09-05
"""

from flask import Blueprint, abort
from sqlalchemy.orm import joinedload
from apifairy.decorators import arguments, response, other_responses

from api import db
from api.models import Play, Song, Artist
from api.decorators import paginated_response
from api.utils.stats import apply_common_filters
from api.utils.arguments import parse_most_played_arguments
from api.schemas import PlaySchema, DateTimePaginationSchema, EmptySchema, PlayStatsArgsSchema


plays = Blueprint('plays', __name__)

play_schema = PlaySchema()
plays_schema = PlaySchema(many=True)


@plays.route('/plays', methods=['GET'])
@paginated_response(plays_schema, order_by=Play.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def list_plays():
    """List all plays"""
    query = (
        db.session.query(Play)
        .options(
            joinedload(Play.song).joinedload(Song.lead_artist)
        )
        .order_by(Play.timestamp.desc())
    )
    return query


@plays.route('/plays/<int:play_id>', methods=['GET'])
@response(play_schema)
@other_responses({404: 'Play not found'})
def get_play(play_id):
    """Retrieve a play by id"""
    return db.session.get(Play, play_id) or abort(404)


@plays.route('/interval', methods=['GET'])
def interval():
    """ Return the dates of the first and last play """
    first_play = db.session.query(Play).order_by(Play.timestamp.asc()).first()
    last_play = db.session.query(Play).order_by(Play.timestamp.desc()).first()
    return {
        'first_play': first_play.timestamp if first_play else None,
        'last_play': last_play.timestamp if last_play else None,
    }


@plays.route('/stats', methods=['GET'])
@arguments(PlayStatsArgsSchema)
def stats(pagination):
    """ Retrieve statistics plays and different songs """
    _, _, radio_id_list, after, before = parse_most_played_arguments(pagination)

    song_search = pagination.get('song_search')
    artist_search = pagination.get('artist_search')

    query = db.session.query(Play).join(Song).join(Artist)

    query = apply_common_filters(
        query,
        id_list=radio_id_list,
        song_search=song_search,
        artist_search=artist_search,
        after=after,
        before=before,
        song_model=Song,
        artist_model=Artist
    )

    total_plays = query.count()
    total_different_songs = query.with_entities(Play.song_id).distinct().count()

    return {
        'total_plays': total_plays,
        'total_different_songs': total_different_songs
    }
