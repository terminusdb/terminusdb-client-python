"""Unit tests for conftest.py helper functions"""

from unittest.mock import patch, Mock
import requests

from .conftest import (
    is_local_server_running,
    is_docker_server_running,
    is_jwt_server_running,
)


class TestServerDetection:
    """Test server detection helper functions"""

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_local_server_running_any_response(self, mock_get):
        """Test local server detection returns True for any HTTP response"""
        mock_get.return_value = Mock()

        assert is_local_server_running() is True
        mock_get.assert_called_once_with("http://127.0.0.1:6363", timeout=2)

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_local_server_running_401(self, mock_get):
        """Test local server detection returns True for HTTP 401 (unauthorized)"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        assert is_local_server_running() is True

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_local_server_not_running_connection_error(self, mock_get):
        """Test local server detection returns False on connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        assert is_local_server_running() is False

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_local_server_not_running_timeout(self, mock_get):
        """Test local server detection returns False on timeout"""
        mock_get.side_effect = requests.exceptions.Timeout()

        assert is_local_server_running() is False

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_docker_server_running_any_response(self, mock_get):
        """Test Docker server detection returns True for any HTTP response"""
        mock_get.return_value = Mock()

        assert is_docker_server_running() is True
        mock_get.assert_called_once_with("http://127.0.0.1:6366", timeout=2)

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_docker_server_running_401(self, mock_get):
        """Test Docker server detection returns True for HTTP 401 (unauthorized)"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        assert is_docker_server_running() is True

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_docker_server_not_running(self, mock_get):
        """Test Docker server detection returns False on connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        assert is_docker_server_running() is False

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_jwt_server_running_any_response(self, mock_get):
        """Test JWT server detection returns True for any HTTP response"""
        mock_get.return_value = Mock()

        assert is_jwt_server_running() is True
        mock_get.assert_called_once_with("http://127.0.0.1:6367", timeout=2)

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_jwt_server_running_401(self, mock_get):
        """Test JWT server detection returns True for HTTP 401 (unauthorized)"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        assert is_jwt_server_running() is True

    @patch("terminusdb_client.tests.integration_tests.conftest.requests.get")
    def test_jwt_server_not_running(self, mock_get):
        """Test JWT server detection returns False on connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        assert is_jwt_server_running() is False
