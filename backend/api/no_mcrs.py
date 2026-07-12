"""
    author: ffpereira
    date: 2025-09-05
"""

from apifairy import response
from sqlalchemy import func, desc
from flask import Blueprint, abort
from apifairy.decorators import other_responses

from api import db
from api.models import NoMcr, Song, Play
from api.decorators import paginated_response
from api.schemas import NoMcrSchema, DateTimePaginationSchema, EmptySchema

no_mcrs = Blueprint('no_mcrs', __name__)

no_mcr_schema = NoMcrSchema()
no_mcrs_schema = NoMcrSchema(many=True)


@no_mcrs.route('/no_mcrs', methods=['GET'])
@paginated_response(no_mcrs_schema, order_by=NoMcr.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def list_no_mcrs():
    """List all no_mcrs"""
    return db.session.query(NoMcr)


@no_mcrs.route('/no_mcrs/<int:no_mcr_id>', methods=['GET'])
@response(no_mcr_schema)
@other_responses({404: 'NoMcr not found'})
def get_no_mcr(no_mcr_id):
    """Retrieve a no_mcr by id"""
    return db.session.get(NoMcr, no_mcr_id) or abort(404)


@no_mcrs.route('/no_mcr_top', methods=['GET'])
def no_mcr_top():
    """Return top X grouped no_mcr entries by item_code, song_name, artist_name"""
    rows = (
        db.session.query(
            NoMcr.item_code.label('item_code'),
            NoMcr.song_name.label('song_name'),
            NoMcr.artist_name.label('artist_name'),
            func.count().label('plays_count')
        )
        .group_by(NoMcr.item_code, NoMcr.song_name, NoMcr.artist_name)
        .order_by(desc('plays_count'))
        .limit(50)
        .all()
    )

    return [
        {
            'item_code': r.item_code,
            'song_name': r.song_name,
            'artist_name': r.artist_name,
            'plays_count': int(r.plays_count),
        }
        for r in rows
    ]

@no_mcrs.route('/no_mcr_to_play/<string:no_mcr_item_code>/<int:song_id>', methods=['POST'])
@response(EmptySchema)
@other_responses({404: 'NoMcr or song not found'})
def no_mcr_to_play(no_mcr_item_code, song_id):
    """ Convert every no_mcr entries of the same song to plays """
    song = db.session.get(Song, song_id) or abort(404)
    no_mcrs = db.session.query(NoMcr).filter(NoMcr.item_code == no_mcr_item_code).all() or abort(404)

    for no_mcr in no_mcrs:
        play = Play(
            radio_id=no_mcr.radio_id,
            song_id=song.id,
            timestamp=no_mcr.timestamp
        )
        db.session.add(play)
        db.session.delete(no_mcr)

    db.session.commit()

    return
