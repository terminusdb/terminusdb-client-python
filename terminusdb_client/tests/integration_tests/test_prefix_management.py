"""Integration tests for prefix management operations."""
import pytest
from terminusdb_client.client import Client


@pytest.fixture
def client():
    """Create a test client connected to TerminusDB."""
    client = Client("http://127.0.0.1:6363")
    client.connect(user="admin", key="root", team="admin")
    return client


@pytest.fixture
def test_db(client):
    """Create and cleanup a test database."""
    import time
    db_name = f"test_prefix_{int(time.time() * 1000)}"
    
    client.create_database(db_name, label="Test Prefix DB", description="Database for testing prefix operations")
    client.connect(db=db_name)
    
    yield db_name
    
    # Cleanup
    try:
        client.delete_database(db_name)
    except Exception:
        pass


class TestPrefixManagement:
    """Test suite for prefix management operations."""

    def test_add_prefix_success(self, client, test_db):
        """Test adding a new prefix successfully."""
        result = client.add_prefix("ex", "http://example.org/")
        assert result["api:status"] == "api:success"
        assert result["api:prefix_name"] == "ex"
        assert result["api:prefix_uri"] == "http://example.org/"

    def test_add_prefix_duplicate(self, client, test_db):
        """Test that adding duplicate prefix fails."""
        client.add_prefix("ex", "http://example.org/")
        
        with pytest.raises(Exception) as exc_info:
            client.add_prefix("ex", "http://example.com/")
        
        # Should get 400 error with PrefixAlreadyExists
        assert exc_info.value.response.status_code == 400

    def test_add_prefix_invalid_iri(self, client, test_db):
        """Test that invalid IRI is rejected."""
        with pytest.raises(Exception) as exc_info:
            client.add_prefix("ex", "not-a-valid-uri")
        
        assert exc_info.value.response.status_code == 400

    def test_add_prefix_reserved(self, client, test_db):
        """Test that reserved prefix names are rejected."""
        with pytest.raises(Exception) as exc_info:
            client.add_prefix("@custom", "http://example.org/")
        
        assert exc_info.value.response.status_code == 400

    def test_get_prefix_success(self, client, test_db):
        """Test retrieving an existing prefix."""
        client.add_prefix("ex", "http://example.org/")
        uri = client.get_prefix("ex")
        assert uri == "http://example.org/"

    def test_get_prefix_not_found(self, client, test_db):
        """Test that getting non-existent prefix fails."""
        with pytest.raises(Exception) as exc_info:
            client.get_prefix("nonexistent")
        
        assert exc_info.value.response.status_code == 404

    def test_update_prefix_success(self, client, test_db):
        """Test updating an existing prefix."""
        client.add_prefix("ex", "http://example.org/")
        result = client.update_prefix("ex", "http://example.com/")
        
        assert result["api:status"] == "api:success"
        assert result["api:prefix_uri"] == "http://example.com/"
        
        # Verify the update
        uri = client.get_prefix("ex")
        assert uri == "http://example.com/"

    def test_update_prefix_not_found(self, client, test_db):
        """Test that updating non-existent prefix fails."""
        with pytest.raises(Exception) as exc_info:
            client.update_prefix("nonexistent", "http://example.org/")
        
        assert exc_info.value.response.status_code == 404

    def test_upsert_prefix_create(self, client, test_db):
        """Test upsert creates prefix if it doesn't exist."""
        result = client.upsert_prefix("ex", "http://example.org/")
        assert result["api:status"] == "api:success"
        assert result["api:prefix_uri"] == "http://example.org/"

    def test_upsert_prefix_update(self, client, test_db):
        """Test upsert updates prefix if it already exists."""
        client.add_prefix("ex", "http://example.org/")
        result = client.upsert_prefix("ex", "http://example.com/")
        
        assert result["api:status"] == "api:success"
        assert result["api:prefix_uri"] == "http://example.com/"

    def test_delete_prefix_success(self, client, test_db):
        """Test deleting an existing prefix."""
        client.add_prefix("ex", "http://example.org/")
        result = client.delete_prefix("ex")
        assert result["api:status"] == "api:success"
        
        # Verify deletion
        with pytest.raises(Exception) as exc_info:
            client.get_prefix("ex")
        assert exc_info.value.response.status_code == 404

    def test_delete_prefix_not_found(self, client, test_db):
        """Test that deleting non-existent prefix fails."""
        with pytest.raises(Exception) as exc_info:
            client.delete_prefix("nonexistent")
        
        assert exc_info.value.response.status_code == 404

    def test_delete_prefix_reserved(self, client, test_db):
        """Test that deleting reserved prefix fails."""
        with pytest.raises(Exception) as exc_info:
            client.delete_prefix("@base")
        
        assert exc_info.value.response.status_code == 400
