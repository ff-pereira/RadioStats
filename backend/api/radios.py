"""
    author: ffpereira
    date: 2025-09-05
"""

from datetime import date
from apifairy import response
from sqlalchemy import func, cast, Date
from apifairy.decorators import other_responses
from flask import Blueprint, abort, request, url_for

from api import db
from api.schemas import RadioSchema, RadioNamesSchema
from api.models import Radio, Play, Artist, Song, OtherArtist
from api.utils.stats import build_daily_counts, finalize_daily_counts, aggregate_total_daily_counts, compute_most_played_periods, compute_time_and_weekday_breakdowns


radios = Blueprint('radios', __name__)

radio_schema = RadioSchema()
radios_schema = RadioSchema(many=True)


@radios.route('/radios', methods=['GET'])
@response(radios_schema)
def list_radios():
    """List all radios"""
    return db.session.query(Radio).order_by(Radio.id.asc())


@radios.route('/radio/<int:radio_id>', methods=['GET'])
@response(radio_schema)
@other_responses({404: 'Radio not found'})
def get_radio(radio_id):
    """Retrieve a radio by id"""
    return db.session.get(Radio, radio_id) or abort(404)


@radios.route('/radio/stats/<int:radio_id>', methods=['GET'])
@other_responses({404: 'Radio not found'})
def radio_stats(radio_id):
    """ Retrieve statistics for a radio by id """
    radio = db.session.get(Radio, radio_id) or abort(404)

    daily_data_query = (
        db.session.query(
            Play.radio_id,
            func.date(Play.timestamp).label("day"),
            func.count().label("plays"),
        )
        .filter(Play.radio_id == radio_id)
    )
    daily_counts, all_dates = build_daily_counts(daily_data_query, [Play.radio_id, "day"])

    for rid, counts in daily_counts.items():
        new_counts = {}
        for d, c in counts.items():
            if isinstance(d, str):
                d = date.fromisoformat(d)
            new_counts[d] = c
        daily_counts[rid] = new_counts

    daily_counts = finalize_daily_counts(daily_counts)

    # Unique songs per day
    unique_songs_query = (
        db.session.query(
            Play.radio_id,
            func.date(Play.timestamp).label("day"),
            func.count(func.distinct(Play.song_id)).label("unique_songs"),
        )
        .filter(Play.radio_id == radio_id)
    )
    unique_songs_daily_counts, _ = build_daily_counts(unique_songs_query, [Play.radio_id, "day"])

    for rid, counts in unique_songs_daily_counts.items():
        new_counts = {}
        for d, c in counts.items():
            if isinstance(d, str):
                d = date.fromisoformat(d)
            new_counts[d] = c
        unique_songs_daily_counts[rid] = new_counts

    unique_songs_daily_counts = finalize_daily_counts(unique_songs_daily_counts)

    # Totals
    play_counts_by_radio = {rid: sum(c.values()) for rid, c in daily_counts.items()}
    total_plays = sum(play_counts_by_radio.values())
    different_songs_count = (
        db.session.query(func.count(func.distinct(Play.song_id)))
        .filter(Play.radio_id == radio_id)
        .scalar()
    )

    normalized_dates = set()
    for d in all_dates:
        if isinstance(d, str):
            d = date.fromisoformat(d)
        normalized_dates.add(d)
    all_dates = normalized_dates

    first_day = min(all_dates).isoformat() if all_dates else None
    last_day = max(all_dates).isoformat() if all_dates else None
    total_days = len(all_dates)

    # Most played
    date_counts = aggregate_total_daily_counts(daily_counts)
    most_played = compute_most_played_periods(date_counts)

    # Time/day breakdowns
    weekday_counts, time_of_day_counts, hourly_counts = compute_time_and_weekday_breakdowns(
        Play.radio_id, [Play.radio_id == radio_id], daily_counts
    )

    return {
        "radio": radio.id,
        "name": radio.name,
        "logo": radio.logo,
        "daily_counts": daily_counts,
        "distinct_songs_daily_counts": unique_songs_daily_counts,
        "total_plays": total_plays,
        "avg_plays_per_song": round(total_plays / different_songs_count, 2) if different_songs_count > 0 else 0,
        "different_songs_count": different_songs_count,
        "play_counts_by_radio": play_counts_by_radio,
        "different_radios_count": len(daily_counts),
        "most_played": most_played,
        "time_of_day_counts": time_of_day_counts,
        "weekday_counts": weekday_counts,
        "hourly_counts": hourly_counts,
        "first_day": first_day,
        "last_day": last_day,
        "total_days": total_days,
    }


@radios.route('/radios/artist/<int:artist_id>', methods=['GET'])
def get_artist_radios(artist_id):
    """Retrieve radio names for an artist based on the lead parameter"""
    lead = request.args.get('lead', '1')

    if lead not in ['0', '1']:
        abort(400, description="Invalid 'lead' parameter. Use '1' for lead or '0' for other.")

    db.session.get(Artist, artist_id) or abort(404)
    if lead == '1':
        radios = (
            db.session.query(Radio)
            .join(Play, Play.radio_id == Radio.id)
            .join(Song, Song.id == Play.song_id)
            .filter(Song.lead_artist_id == artist_id)
            .distinct()
            .all()
        )
    else:
        radios = (
            db.session.query(Radio)
            .join(Play, Play.radio_id == Radio.id)
            .join(Song, Song.id == Play.song_id)
            .join(OtherArtist, OtherArtist.song_id == Song.id)
            .filter(OtherArtist.artist_id == artist_id)
            .distinct()
            .all()
        )

    return {"radio_names": {radio.id: url_for('static', filename=f"images/radios/{radio.id}.jpg", _external=True) for radio in radios}}


@radios.route('/radios/song/<int:song_id>', methods=['GET'])
def get_song_radios(song_id):
    """Retrieve radio names for a song"""

    db.session.get(Song, song_id) or abort(404)

    radios = (
        db.session.query(Radio)
        .join(Play, Play.radio_id == Radio.id)
        .join(Song, Song.id == Play.song_id)
        .filter(Song.id == song_id)
        .distinct()
        .all()
    )

    return {"radio_names": {radio.id: url_for('static', filename=f"images/radios/{radio.id}.jpg", _external=True) for radio in radios}}
