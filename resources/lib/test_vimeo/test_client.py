__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.vimeo.client import Client

import unittest


class TestClient(unittest.TestCase):
    USERNAME = ''
    PASSWORD = ''

    def get_client(self, logged_in=False):
        client = Client()
        return client

    def test_create_authorization(self):
        client = self.get_client()
        params = {'method': 'vimeo.videos.search',
                  'sort': 'relevant',
                  'page': '1',
                  'summary_response': '1',
                  'query': 'superman'}
                  #'oauth_timestamp': '1425165588',
                  #'oauth_nonce': '720610187562182'}
        oauth = client._create_authorization(url='http://vimeo.com/api/rest/v2',
                                             method='POST',
                                             params=params)
        pass

    def test_search(self):
        client = self.get_client()
        xml_data = client.search(query='daredevil')
        pass

    def test_featured(self):
        client = self.get_client()
        xml_data = client.get_featured()
        pass

    pass
