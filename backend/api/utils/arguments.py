"""
    author: ffpereira
    date: 2025-09-05
"""

from flask import abort
from datetime import datetime


def parse_most_played_arguments(pagination, max_limit=25):
    """ Parse and validate pagination arguments for most_played endpoints """
    limit = min(pagination.get('limit', 25), max_limit)
    offset = pagination.get('offset', 0)
    radio_ids = pagination.get('radios')
    radio_id_list = [int(radio_id.strip()) for radio_id in radio_ids.split(',') if radio_id.strip().isdigit()] if radio_ids else []

    def parse_dt(field):
        val = pagination.get(field)
        if not val:
            return None
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            abort(400, description=f"Invalid '{field}' datetime format. Use ISO 8601 format.")

    after, before = parse_dt('after'), parse_dt('before')
    if after and before and after >= before:
        abort(400, description="'after' must be earlier than 'before'.")
    return limit, offset, radio_id_list, after, before
