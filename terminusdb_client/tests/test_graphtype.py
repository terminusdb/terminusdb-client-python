"""Unit tests for GraphType enum"""
from terminusdb_client.client import GraphType


class TestGraphType:
    """Test GraphType enum values"""

    def test_graphtype_instance(self):
        """Test GraphType.INSTANCE value"""
        assert GraphType.INSTANCE == "instance"

    def test_graphtype_schema(self):
        """Test GraphType.SCHEMA value"""
        assert GraphType.SCHEMA == "schema"

    def test_graphtype_enum_members(self):
        """Test GraphType has exactly two members"""
        members = list(GraphType)
        assert len(members) == 2
        assert GraphType.INSTANCE in members
        assert GraphType.SCHEMA in members

    def test_graphtype_values(self):
        """Test all GraphType enum values exist"""
        assert hasattr(GraphType, 'INSTANCE')
        assert hasattr(GraphType, 'SCHEMA')
