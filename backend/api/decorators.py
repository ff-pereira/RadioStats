
from flask import abort
import sqlalchemy as sqla
from functools import wraps
from apifairy import arguments, response

from api.app import db
from api.schemas import StringPaginationSchema, PaginatedCollection


def paginated_response(schema, max_limit=25, order_by=None,
                       order_direction='asc',
                       pagination_schema=StringPaginationSchema):
    def inner(f):
        @wraps(f)
        def paginate(*args, **kwargs):
            args = list(args)
            pagination = args.pop(-1)
            select_query = f(*args, **kwargs)

            if order_by is not None:
                o = order_by.desc() if order_direction == 'desc' else order_by
                select_query = select_query.order_by(o)

            count = db.session.scalar(sqla.select(sqla.func.count()).select_from(select_query.subquery()))

            limit = pagination.get('limit', max_limit)
            offset = pagination.get('offset')
            after = pagination.get('after')
            before = pagination.get('before')

            if limit > max_limit:
                limit = max_limit
            if after is not None or before is not None:
                if offset is not None or order_by is None:
                    abort(400)

                filters = []
                offset_filters = []

                if after is not None and before is not None and after >= before:
                    abort(400)

                if after is not None:
                    filters.append(order_by > after)
                    offset_filters.append(order_by <= after)

                if before is not None:
                    filters.append(order_by < before)
                    offset_filters.append(order_by >= before)

                # query = select_query.limit(limit).filter(*filters)
                query = select_query.filter(*filters).limit(limit)
                offset = db.session.scalar(sqla.select(sqla.func.count()).select_from(select_query.filter(*offset_filters).subquery()))
            else:
                if offset is None:
                    offset = 0
                if offset < 0 or (count > 0 and offset >= count) or limit <= 0:
                    abort(400)

                query = select_query.limit(limit).offset(offset)

            stmt = sqla.select(query.column_descriptions[0]['entity']).offset(offset).limit(limit)
            data = db.session.scalars(stmt).all()

            return {'data': data, 'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(data),
                'total': count,
            }}

        # wrap with APIFairy's arguments and response decorators
        return arguments(pagination_schema)(response(PaginatedCollection(
            schema, pagination_schema=pagination_schema))(paginate))

    return inner
