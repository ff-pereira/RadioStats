"""
    author: ffpereira
    date: 2025-09-05
"""

import calendar
from collections import defaultdict
from datetime import date, timedelta
from sqlalchemy import func, case, extract

from api import db
from api.models import Play


def apply_common_filters(query, id_list=None, song_search=None, artist_search=None, after=None, before=None, song_model=None, artist_model=None):
    """ Apply common filters to a SQLAlchemy query for Play records """
    if id_list:
        query = query.filter(Play.radio_id.in_(id_list))
    if song_search and song_model:
        query = query.filter(song_model.name.ilike(f'%{song_search}%'))
    if artist_search and artist_model:
        query = query.filter(artist_model.name.ilike(f'%{artist_search}%'))
    if after is not None:
        query = query.filter(Play.timestamp > after)
    if before is not None:
        query = query.filter(Play.timestamp < before)
    return query


def get_date_range_days(id_list=None, after=None, before=None):
    """ Return number of days in date range for given filters """
    date_range_query = db.session.query(
        func.min(Play.timestamp).label("min_date"),
        func.max(Play.timestamp).label("max_date")
    )
    if id_list:
        date_range_query = date_range_query.filter(Play.radio_id.in_(id_list))
    if after is not None:
        date_range_query = date_range_query.filter(Play.timestamp > after)
    if before is not None:
        date_range_query = date_range_query.filter(Play.timestamp < before)

    date_range = date_range_query.one()
    return (date_range.max_date - date_range.min_date).days + 1


def build_pagination_metadata(offset, limit, results, total_count):
    """ Build pagination metadata dictionary """
    return {
        'offset': offset,
        'limit': limit,
        'count': len(results),
        'total': total_count
    }


def build_daily_counts(query, group_fields):
    """
    Execute a query grouped by given fields and return nested daily_counts dict.
    Example output: {group_key: {day: plays}}
    """
    daily_data = query.group_by(*group_fields).all()
    daily_counts = defaultdict(lambda: defaultdict(int))
    all_dates = set()

    for *keys, day, plays in daily_data:
        key = tuple(keys) if len(keys) > 1 else keys[0]
        daily_counts[key][day] = plays
        all_dates.add(day)

    return daily_counts, all_dates


def fill_date_gaps(daily_counts):
    """Ensure continuity of daily counts across date range."""
    all_dates = {d for counts in daily_counts.values() for d in counts.keys()}

    if all_dates:
        min_date = min(all_dates)
        max_date = date.today() - timedelta(days=1)
        full_range = [
            min_date + timedelta(days=i)
            for i in range((max_date - min_date).days + 1)
        ]

        for key in daily_counts:
            for d in full_range:
                if d not in daily_counts[key]:
                    daily_counts[key][d] = 0

    return daily_counts


def sort_and_format_dates(daily_counts):
    """Sort by date and convert datetime.date → iso string."""
    return {
        key: {d.isoformat(): c for d, c in sorted(counts.items())}
        for key, counts in daily_counts.items()
    }


def finalize_daily_counts(daily_counts):
    """Fill missing dates and return ISO-sorted date keys."""
    return sort_and_format_dates(fill_date_gaps(daily_counts))


def aggregate_total_daily_counts(daily_counts):
    """Flatten nested daily counts {entity: {day: plays}} → {day: total plays}."""
    total_daily = defaultdict(int)
    for counts in daily_counts.values():
        for day_str, count in counts.items():
            total_daily[day_str] += count
    return {date.fromisoformat(d): c for d, c in total_daily.items()}


def find_max_items(count_dict):
    """Return all items with the max count."""
    max_count = max(count_dict.values(), default=0)
    return [(k, v) for k, v in count_dict.items() if v == max_count]


def aggregate_by_period(date_counts):
    """Aggregate counts by day, week, month, year."""
    week_counts = defaultdict(int)
    month_counts = defaultdict(int)
    year_counts = defaultdict(int)

    for d, c in date_counts.items():
        week_counts[d.isocalendar()[:2]] += c
        month_counts[(d.year, d.month)] += c
        year_counts[d.year] += c

    return week_counts, month_counts, year_counts


def iso_week_to_range(year, week):
    """Convert ISO week to date range string."""
    monday = date.fromisocalendar(year, week, 1)
    sunday = date.fromisocalendar(year, week, 7)
    return f"{monday.isoformat()} to {sunday.isoformat()}"


def compute_most_played_periods(date_counts):
    """Return structured dict of most played day/week/month/year periods."""
    week_counts, month_counts, year_counts = aggregate_by_period(date_counts)

    return {
        "day": [{"value": d.isoformat(), "count": c} for d, c in find_max_items(date_counts)],
        "week": [{"value": iso_week_to_range(y, w), "count": c} for (y, w), c in find_max_items(week_counts)],
        "month": [{"value": f"{y}-{m:02d}", "count": c} for (y, m), c in find_max_items(month_counts)],
        "year": [{"value": str(y), "count": c} for y, c in find_max_items(year_counts)],
    }


def query_time_of_day_counts(filter_clause):
    """Query play counts grouped by time of day (dawn/morning/afternoon/night)."""
    q = (
        db.session.query(
            case(
                (extract('hour', Play.timestamp).between(0, 5), 'dawn'),
                (extract('hour', Play.timestamp).between(6, 11), 'morning'),
                (extract('hour', Play.timestamp).between(12, 17), 'afternoon'),
                (extract('hour', Play.timestamp).between(18, 23), 'night'),
            ).label('period'),
            func.count().label('plays')
        )
        .filter(*filter_clause)
        .group_by('period')
    )
    return {period: count for period, count in q.all()}


def query_hourly_counts(group_field, filter_clause):
    """Query play counts grouped by hour."""
    q = (
        db.session.query(
            group_field,
            extract('hour', Play.timestamp).label('hour'),
            func.count().label('plays')
        )
        .filter(*filter_clause)
        .group_by(group_field, 'hour')
    )

    hourly_counts = defaultdict(lambda: defaultdict(int))
    for key, hour, count in q.all():
        hourly_counts[key][int(hour)] = count

    return {
        key: {h: c for h, c in sorted(counts.items())}
        for key, counts in hourly_counts.items()
    }


def weekday_aggregate(daily_counts):
    """Aggregate total plays by weekday (Monday–Sunday)."""
    weekday_counts = defaultdict(lambda: defaultdict(int))
    for key, counts in daily_counts.items():
        for day_str, count in counts.items():
            day_obj = date.fromisoformat(day_str)
            weekday_name = calendar.day_name[day_obj.weekday()]
            weekday_counts[key][weekday_name] += count
    return weekday_counts


def compute_time_and_weekday_breakdowns(group_field, base_filters, daily_counts):
    """Convenience wrapper for weekday, time-of-day, and hourly breakdowns."""
    weekday_counts = weekday_aggregate(daily_counts)
    time_of_day_counts = query_time_of_day_counts(base_filters)
    hourly_counts = query_hourly_counts(group_field, base_filters)
    return weekday_counts, time_of_day_counts, hourly_counts
