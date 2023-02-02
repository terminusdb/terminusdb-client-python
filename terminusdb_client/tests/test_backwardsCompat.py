# import sys
# sys.path.append('client')
import unittest.mock as mock
from .conftest import mocked_request_success
from ..__version__ import __version__

import requests

from terminusdb_client.woqlclient import WOQLClient


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_connection(mocked_requests):
    client = WOQLClient("http://localhost:6363")

    client.connect(key="root", team="admin", user="admin")

    client._session.get.assert_called_once_with(
        "http://localhost:6363/api/info",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )
