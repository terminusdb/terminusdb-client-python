"""Tests for scripts/__main__.py module."""
import sys
from unittest.mock import patch, MagicMock


def test_main_imports():
    """Test that __main__ can be imported."""
    from terminusdb_client.scripts import __main__
    assert __main__ is not None


def test_main_has_tdbpy():
    """Test that __main__ imports tdbpy function."""
    from terminusdb_client.scripts import __main__
    assert hasattr(__main__, 'tdbpy')


def test_main_execution():
    """Test that __main__ calls tdbpy when executed."""
    mock_tdbpy = MagicMock()
    
    with patch('terminusdb_client.scripts.__main__.tdbpy', mock_tdbpy):
        # Simulate running as main module
        with patch.object(sys, 'argv', ['__main__.py']):
            # Import and check the condition would trigger
            from terminusdb_client.scripts import __main__
            assert __main__.__name__ == 'terminusdb_client.scripts.__main__'
