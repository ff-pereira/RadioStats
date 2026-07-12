"""
    author: ffpereira
    date: 2025-09-05
"""

from tests.base_test_case import BaseTestCase


class RouteTests(BaseTestCase):
    def test_index_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
