"""
    author: ffpereira
    date: 2025-09-05
"""

from api import ma
from api.schemas import PaginatedCollection
from tests.base_test_case import BaseTestCase


class ModelTests(BaseTestCase):

    def test_paginated_collection_caches_schema(self):
        class MySchema(ma.Schema):
            field = ma.String()

        first = PaginatedCollection(MySchema)
        second = PaginatedCollection(MySchema)

        assert first is second

        schema_instance = first()
        assert 'data' in schema_instance.fields
        assert 'pagination' in schema_instance.fields

    #         print(json.dumps(rv.get_json(), indent=2))
