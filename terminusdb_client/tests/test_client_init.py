"""Unit tests for Client initialization"""
from terminusdb_client.client import Client


class TestClientInitialization:
    """Test Client initialization and basic properties"""

    def test_client_init_basic(self):
        """Test basic Client initialization"""
        client = Client("http://localhost:6363")
        assert client.server_url == "http://localhost:6363"
        assert client._connected is False

    def test_client_init_with_user_agent(self):
        """Test Client initialization with custom user agent"""
        client = Client("http://localhost:6363", user_agent="test-agent/1.0")
        assert "test-agent/1.0" in client._default_headers.get("user-agent", "")

    def test_client_init_with_trailing_slash(self):
        """Test Client handles URLs with trailing slashes"""
        client = Client("http://localhost:6363/")
        # Should work without errors
        assert client.server_url in ["http://localhost:6363", "http://localhost:6363/"]

    def test_client_copy(self):
        """Test Client copy method creates independent instance"""
        client1 = Client("http://localhost:6363")
        client1.team = "test_team"
        client1.db = "test_db"

        client2 = client1.copy()

        assert client2.server_url == client1.server_url
        assert client2.team == client1.team
        assert client2.db == client1.db
        # Ensure it's a different object
        assert client2 is not client1

    def test_client_copy_modifications_independent(self):
        """Test modifications to copied client don't affect original"""
        client1 = Client("http://localhost:6363")
        client1.team = "team1"

        client2 = client1.copy()
        client2.team = "team2"

        assert client1.team == "team1"
        assert client2.team == "team2"
