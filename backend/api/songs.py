"""
    author: ffpereira
    date: 2025-09-05
"""

from datetime import date
from apifairy import response
from sqlalchemy import func, cast, Date
from flask import Blueprint, abort, url_for
from apifairy.decorators import other_responses, arguments

from api import db
from api.decorators import paginated_response
from api.models import Song, Play, Artist, Radio
from api.utils.arguments import parse_most_played_arguments
from api.schemas import (SongSchema, MostPlayedSongSchema, PaginatedCollection, MostPlayedPaginationSchema,
                         StatsPaginationSchema, StringPaginationSchema, SongStatsResponseSchema)
from api.utils.stats import (apply_common_filters, get_date_range_days, build_pagination_metadata, build_daily_counts, finalize_daily_counts,
                             aggregate_total_daily_counts, compute_most_played_periods, compute_time_and_weekday_breakdowns)


songs = Blueprint('songs', __name__)

song_schema = SongSchema()
songs_schema = SongSchema(many=True)
most_played_song_schema = MostPlayedSongSchema(many=True)


@songs.route('/songs', methods=['GET'])
@paginated_response(songs_schema, order_by=Song.name,
                    order_direction='asc',
                    pagination_schema=StringPaginationSchema)
def list_songs():
    """List all songs"""
    return db.session.query(Song)


@songs.route('/song/<int:song_id>', methods=['GET'])
@response(song_schema)
@other_responses({404: 'Song not found'})
def get_song(song_id):
    """Retrieve a song by id"""
    return db.session.get(Song, song_id) or abort(404)


@songs.route('/songs/most_played', methods=['GET'])
@arguments(MostPlayedPaginationSchema)
@response(PaginatedCollection(most_played_song_schema, pagination_schema=StringPaginationSchema))
def most_played(pagination):
    """ Retrieve most played songs """
    limit, offset, radio_id_list, after, before = parse_most_played_arguments(pagination)
    song_search = pagination.get('song_search')
    artist_search = pagination.get('artist_search')

    query = (
        db.session.query(
            Song.id.label('song_id'),
            Song.name.label('song_name'),
            Song.album_id.label('album_id'),
            Song.lead_artist_id.label('artist_id'),
            Artist.name.label('artist_name'),
            func.count(Play.id).label('play_count'),
            func.count().over().label('total_count')
        )
        .join(Play, Play.song_id == Song.id)
        .join(Artist, Artist.id == Song.lead_artist_id)
        .group_by(Song.id, Song.name, Song.album_id, Song.lead_artist_id, Artist.name)
    )

    query = apply_common_filters(query, radio_id_list, song_search, artist_search, after, before, Song, Artist)
    subquery = query.subquery()

    results = (
        db.session.query(
            subquery.c.song_id,
            subquery.c.song_name,
            subquery.c.album_id,
            subquery.c.artist_id,
            subquery.c.artist_name,
            subquery.c.play_count,
            subquery.c.total_count
        )
        .order_by(subquery.c.play_count.desc(), subquery.c.song_id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_count = results[0].total_count if results else 0
    days = get_date_range_days(radio_id_list, after, before)

    return {
        'data': [
            {
                'id': r.song_id,
                'song_name': r.song_name,
                'album_id': r.album_id,
                'artist_id': r.artist_id,
                'artist_name': r.artist_name,
                'play_count': r.play_count,
                'avg_per_day': round(r.play_count / days, 2) if days else 0,
                'album_cover_url': url_for('static', filename=f"images/albums/{r.album_id}.jpg", _external=True) if r.album_id else None,
                'sample': url_for('static', filename=f"samples/{r.song_id}.mp4", _external=True)
            }
            for r in results
        ],
        'pagination': build_pagination_metadata(offset, limit, results, total_count)
    }


@songs.route('/song/stats/<int:song_id>', methods=['GET'])
@arguments(StatsPaginationSchema)
@response(SongStatsResponseSchema)
@other_responses({404: 'Song not found'})
def song_stats(args, song_id):
    """ Retrieve statistics for a song by id """
    song = db.session.get(Song, song_id) or abort(404)

    radio_ids = args.get('radios', '')
    radio_id_list = [int(r.strip()) for r in radio_ids.split(',') if r.strip().isdigit()]

    radios = db.session.query(Radio).all()
    radio_names = {r.id: r.name for r in radios}

    # Daily aggregation
    daily_data_query = (
        db.session.query(
            Play.radio_id,
            func.date(Play.timestamp).label("day"),
            func.count().label("plays"),
        )
        .filter(Play.song_id == song_id)
    )
    if radio_id_list:
        daily_data_query = daily_data_query.filter(Play.radio_id.in_(radio_id_list))

    daily_counts, _ = build_daily_counts(daily_data_query, [Play.radio_id, "day"])

    for rid, counts in daily_counts.items():
        new_counts = {}
        for d, c in counts.items():
            if isinstance(d, str):
                d = date.fromisoformat(d)
            new_counts[d] = c
        daily_counts[rid] = new_counts

    daily_counts = finalize_daily_counts(daily_counts)

    # Totals
    play_counts_by_radio = [
        {"radio_id": rid, "count": sum(counts.values()), "name": radio_names.get(rid, f"Radio {rid}")}
        for rid, counts in daily_counts.items()
    ]
    play_counts_by_radio.sort(key=lambda x: x["count"], reverse=True)
    total_plays = sum(x["count"] for x in play_counts_by_radio)

    # Most played
    date_counts = aggregate_total_daily_counts(daily_counts)
    most_played = compute_most_played_periods(date_counts)

    # Time/day breakdowns
    base_filters = [Play.song_id == song_id]
    if radio_id_list:
        base_filters.append(Play.radio_id.in_(radio_id_list))
    weekday_counts, time_of_day_counts, hourly_counts = compute_time_and_weekday_breakdowns(
        Play.radio_id, base_filters, daily_counts
    )

    return {
        "song_id": song.id,
        "daily_counts": daily_counts,
        "total_plays": total_plays,
        "radio_names": radio_names,
        "play_counts_by_radio": play_counts_by_radio,
        "different_radios_count": len(daily_counts),
        "most_played": most_played,
        "time_of_day_counts": time_of_day_counts,
        "weekday_counts": weekday_counts,
        "hourly_counts": hourly_counts,
    }


@songs.route('/song/ranking/<int:song_id>', methods=['GET'])
@arguments(StatsPaginationSchema)
@other_responses({404: 'Song not found'})
def song_ranking(args, song_id):
    """Retrieve the rank and percentile of a song by id"""
    radio_ids = args.get('radios', '')
    radio_id_list = [int(r.strip()) for r in radio_ids.split(',') if r.strip().isdigit()]

    query = (
        db.session.query(
            Song.id.label('song_id'),
            func.rank().over(order_by=func.count(Play.id).desc()).label('rank'),
            func.count().over().label('total_count')
        )
        .join(Play, Play.song_id == Song.id)
        .group_by(Song.id)
    )

    if radio_id_list:
        query = query.filter(Play.radio_id.in_(radio_id_list))

    subquery = query.subquery()

    result = db.session.query(subquery.c.rank, subquery.c.total_count).filter(subquery.c.song_id == song_id).first()

    if not result:
        abort(404, description="Song not found")

    rank = result.rank
    total_count = result.total_count
    percentile = round((rank / total_count) * 100, 2)

    return {
        'rank': rank,
        'percentile': percentile,
    }
