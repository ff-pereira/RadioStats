"""
    author: ffpereira
    date: 2025-09-05
"""

from datetime import date
from apifairy import response
from flask import Blueprint, abort, request
from sqlalchemy import func, distinct, cast, Date, desc
from apifairy.decorators import other_responses, arguments

from api import db
from api.decorators import paginated_response
from api.utils.arguments import parse_most_played_arguments
from api.models import Song, Artist, OtherArtist, Play, Album, Radio
from api.schemas import (ArtistSchema, EmptySchema, StringPaginationSchema, MostPlayedArtistSchema, PaginatedCollection,
                         MostPlayedPaginationSchema, ArtistStatsArgsSchema, SongSchema, ArtistStatsResponseSchema)
from api.utils.stats import (apply_common_filters,get_date_range_days,build_pagination_metadata, build_daily_counts, finalize_daily_counts,
                             aggregate_total_daily_counts, compute_most_played_periods, compute_time_and_weekday_breakdowns)



artists = Blueprint('artists', __name__)

artist_schema = ArtistSchema()
artists_schema = ArtistSchema(many=True)
most_played_artist_schema = MostPlayedArtistSchema(many=True)


@artists.route('/artists', methods=['GET'])
@paginated_response(artists_schema, order_by=Artist.name,
                    order_direction='asc',
                    pagination_schema=StringPaginationSchema)
def list_artists():
    """List all artists"""
    return db.session.query(Artist)


@artists.route('/artist/<int:artist_id>', methods=['GET'])
@response(artist_schema)
@other_responses({404: 'Artist not found'})
def get_artist(artist_id):
    """Retrieve an artist by id"""
    return db.session.get(Artist, artist_id) or abort(404)


@artists.route('/artists/most_played', methods=['GET'])
@arguments(MostPlayedPaginationSchema)
@response(PaginatedCollection(MostPlayedArtistSchema, pagination_schema=StringPaginationSchema))
def most_played_artists(pagination):
    """ Retrieve most played artists """
    limit, offset, radio_id_list, after, before = parse_most_played_arguments(pagination)
    song_search = pagination.get('song_search')
    artist_search = pagination.get('artist_search')

    lead_subquery = (
        db.session.query(
            Artist.id.label('artist_id'),
            Artist.name.label('artist_name'),
            func.count(Play.id).label('play_count'),
            func.count(distinct(Song.id)).label('different_songs'),
            func.count(distinct(Song.album_id)).label('different_albums'),
            func.count().over().label('total_count')
        )
        .join(Song, Song.lead_artist_id == Artist.id)
        .join(Play, Play.song_id == Song.id)
        .group_by(Artist.id, Artist.name)
    )

    other_subquery = (
        db.session.query(
            OtherArtist.artist_id.label('artist_id'),
            Artist.name.label('artist_name'),
            func.count(Play.id).label('play_count'),
            func.count(distinct(Song.id)).label('different_songs'),
            func.count(distinct(Song.album_id)).label('different_albums')
        )
        .join(Artist, Artist.id == OtherArtist.artist_id)
        .join(Song, Song.id == OtherArtist.song_id)
        .join(Play, Play.song_id == Song.id)
        .group_by(OtherArtist.artist_id, Artist.name)
    )

    lead_subquery = apply_common_filters(lead_subquery, radio_id_list, song_search, artist_search, after, before, Song, Artist)
    other_subquery = apply_common_filters(other_subquery, radio_id_list, song_search, artist_search, after, before, Song, Artist)

    lead_subquery = lead_subquery.subquery()
    other_subquery = other_subquery.subquery()

    results = (
        db.session.query(
            lead_subquery.c.artist_id,
            lead_subquery.c.artist_name,
            lead_subquery.c.play_count.label('lead_play_count'),
            lead_subquery.c.different_songs.label('lead_different_songs'),
            lead_subquery.c.different_albums.label('lead_different_albums'),
            lead_subquery.c.total_count,
            func.coalesce(other_subquery.c.play_count, 0).label('other_play_count'),
            func.coalesce(other_subquery.c.different_songs, 0).label('other_different_songs'),
            func.coalesce(other_subquery.c.different_albums, 0).label('other_different_albums')
        )
        .outerjoin(other_subquery, other_subquery.c.artist_id == lead_subquery.c.artist_id)
        .order_by((lead_subquery.c.play_count + func.coalesce(other_subquery.c.play_count, 0)).desc(), lead_subquery.c.artist_id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_count = results[0].total_count if results else 0
    days = get_date_range_days(radio_id_list, after, before)

    return {
        'data': [
            {
                'id': r.artist_id,
                'name': r.artist_name,
                'lead': {
                    'play_count': r.lead_play_count,
                    'songs': r.lead_different_songs,
                    'albums': r.lead_different_albums,
                },
                'other': {
                    'play_count': r.other_play_count,
                    'songs': r.other_different_songs,
                    'albums': r.other_different_albums,
                },
                "different_songs": r.lead_different_songs + r.other_different_songs,
                "count": r.lead_play_count + r.other_play_count,
                "avg_per_day": round((r.lead_play_count + r.other_play_count) / days, 2) if days else 0,
            }
            for r in results
        ],
        'pagination': build_pagination_metadata(offset, limit, results, total_count)
    }


@artists.route('/artist/stats/<int:artist_id>', methods=['GET'])
@arguments(ArtistStatsArgsSchema)
@response(ArtistStatsResponseSchema)
@other_responses({404: 'Artist not found'})
def artist_stats(args, artist_id):
    """ Retrieve statistics for an artist by id """
    artist = db.session.get(Artist, artist_id) or abort(404)

    radio_ids = args.get('radios')
    radio_id_list = [int(r.strip()) for r in radio_ids.split(',') if r.strip().isdigit()] if radio_ids else []
    is_lead = args.get('lead', True)

    # Retrieve songs
    if radio_id_list:
        base_query = (
            db.session.query(Song)
            .join(Play, Play.song_id == Song.id)
            .filter(Play.radio_id.in_(radio_id_list))
            .distinct()
        )
        if is_lead:
            songs = base_query.filter(Song.lead_artist_id == artist_id).all()
        else:
            songs = (
                base_query
                .join(OtherArtist, OtherArtist.song_id == Song.id)
                .filter(OtherArtist.artist_id == artist_id)
                .all()
            )
    else:
        songs = artist.songs if is_lead else artist.songs_as_other

    if not songs:
        return {
            "artist_id": artist_id,
            "total_plays": 0,
            "daily_counts": {},
            "play_counts_by_song": [],
            "different_songs_count": 0,
            "most_played": {"day": [], "week": [], "month": [], "year": []},
            "time_of_day_counts": {},
            "weekday_counts": {},
            "hourly_counts": {},
        }

    song_ids = [s.id for s in songs]
    songs_dic = {s.id: s.name for s in songs}

    # Aggregate daily data
    daily_data_query = (
        db.session.query(
            Play.song_id,
            func.date(Play.timestamp).label("day"),
            func.count().label("plays"),
        )
        .filter(Play.song_id.in_(song_ids))
    )
    if radio_id_list:
        daily_data_query = daily_data_query.filter(Play.radio_id.in_(radio_id_list))

    daily_counts, _ = build_daily_counts(daily_data_query, [Play.song_id, "day"])

    for rid, counts in daily_counts.items():
        new_counts = {}
        for d, c in counts.items():
            if isinstance(d, str):
                d = date.fromisoformat(d)
            new_counts[d] = c
        daily_counts[rid] = new_counts

    daily_counts = finalize_daily_counts(daily_counts)

    # Totals
    play_counts_by_song_totals = {sid: sum(counts.values()) for sid, counts in daily_counts.items()}
    total_plays = sum(play_counts_by_song_totals.values())

    # Serialize
    song_schema = SongSchema()
    play_counts_by_song = sorted(
        [
            {**song_schema.dump(s), "play_count": play_counts_by_song_totals.get(s.id, 0)}
            for s in songs
        ],
        key=lambda x: x["play_count"],
        reverse=True,
    )

    # Aggregate across all songs
    date_counts = aggregate_total_daily_counts(daily_counts)
    most_played = compute_most_played_periods(date_counts)

    # Time/day breakdowns
    base_filters = [Play.song_id.in_(song_ids)]
    if radio_id_list:
        base_filters.append(Play.radio_id.in_(radio_id_list))
    weekday_counts, time_of_day_counts, hourly_counts = compute_time_and_weekday_breakdowns(
        Play.song_id, base_filters, daily_counts
    )

    return {
        "artist_id": artist_id,
        "total_plays": total_plays,
        "daily_counts": daily_counts,
        "play_counts_by_song": play_counts_by_song,
        "different_songs_count": len(song_ids),
        "avg_plays_per_song": round(total_plays / len(song_ids), 2) if song_ids else 0,
        "song_names": songs_dic,
        "most_played": most_played,
        "time_of_day_counts": time_of_day_counts,
        "weekday_counts": weekday_counts,
        "hourly_counts": hourly_counts,
    }


@artists.route('/artist/ranking/<int:artist_id>', methods=['GET'])
@arguments(ArtistStatsArgsSchema)
@other_responses({404: 'Artist not found'})
def artist_ranking(args, artist_id):
    """Retrieve the rank and percentile of an artist by id"""
    radio_ids = args.get('radios', '')
    radio_id_list = [int(r.strip()) for r in radio_ids.split(',') if r.strip().isdigit()]
    lead = args.get('lead', True)

    query = db.session.query(
        Artist.id.label('artist_id'),
        func.rank().over(order_by=func.count(Play.id).desc()).label('rank'),
        func.count().over().label('total_count')
    )

    if lead:
        query = query.join(Song, Song.lead_artist_id == Artist.id)
    else:
        query = (
            query
            .join(OtherArtist, OtherArtist.artist_id == Artist.id)
            .join(Song, Song.id == OtherArtist.song_id)
        )

    query = query.join(Play, Play.song_id == Song.id).group_by(Artist.id)

    if radio_id_list:
        query = query.filter(Play.radio_id.in_(radio_id_list))

    subquery = query.subquery()

    result = db.session.query(subquery.c.rank, subquery.c.total_count).filter(subquery.c.artist_id == artist_id).first()

    if not result:
        abort(404, description="Artist not found")

    rank = result.rank
    total_count = result.total_count
    percentile = round((rank / total_count) * 100, 2)

    return {
        'rank': rank,
        'percentile': percentile,
    }


@artists.route('/no_description_top', methods=['GET'])
def no_description_top():
    """Return top X artists without description"""
    rows = (
        db.session.query(
            Artist.id.label('artist_id'),
            Artist.name.label('artist_name'),
            Artist.nationality,
            Artist.description,
            func.count(Play.id).label('plays_count')
        )
        .join(Song, Song.lead_artist_id == Artist.id)
        .join(Play, Play.song_id == Song.id)
        .filter(Artist.description.is_(None) | (Artist.nationality.is_(None)) )
        .group_by(Artist.id, Artist.name)
        .order_by(desc('plays_count'))
        .limit(100)
        .all()
    )

    return [
        {
            'artist_id': r.artist_id,
            'artist_name': r.artist_name,
            'nationality': r.nationality,
            'description': r.description,
            'plays_count': int(r.plays_count),
        }
        for r in rows
    ]


@artists.route('/update_artist/<int:artist_id>', methods=['POST'])
@response(EmptySchema)
@other_responses({404: 'Artist not found'})
def update_artist(artist_id):
    """ Update nationality and/or description of an artist """
    data = request.json or {}
    nationality = data.get("nationality")
    description = data.get("description")

    artist = db.session.get(Artist, artist_id) or abort(404)

    if nationality:
        artist.nationality = nationality
    if description:
        artist.description = description

    db.session.add(artist)
    db.session.commit()
    return
