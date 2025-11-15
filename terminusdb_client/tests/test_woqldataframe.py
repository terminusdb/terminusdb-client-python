"""Tests for woqldataframe/woqlDataframe.py module."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from terminusdb_client.woqldataframe.woqlDataframe import result_to_df
from terminusdb_client.errors import InterfaceError


def test_result_to_df_requires_pandas():
    """Test that result_to_df raises ImportError when pandas is not available."""
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module') as mock_import:
        mock_import.side_effect = ImportError("No module named 'pandas'")
        
        with pytest.raises(ImportError) as exc_info:
            result_to_df([{"@id": "test", "@type": "Test"}])
        
        assert "pandas" in str(exc_info.value).lower()
        assert "terminus-client-python[dataframe]" in str(exc_info.value)


def test_result_to_df_requires_client_with_max_embed():
    """Test that result_to_df raises ValueError when max_embed_dep > 0 without client."""
    mock_pd = MagicMock()
    mock_pd.DataFrame.return_value.from_records.return_value = mock_pd.DataFrame.return_value
    
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module', return_value=mock_pd):
        with pytest.raises(ValueError) as exc_info:
            result_to_df([{"@id": "test", "@type": "Test"}], max_embed_dep=1)
        
        assert "client need to be provide" in str(exc_info.value)


def test_result_to_df_multiple_types_error():
    """Test that result_to_df raises ValueError for multiple document types."""
    mock_pd = MagicMock()
    
    # Create mock DataFrame with multiple types
    mock_df = MagicMock()
    mock_df.__getitem__.return_value.unique.return_value = ["Type1", "Type2"]
    mock_pd.DataFrame.return_value.from_records.return_value = mock_df
    
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module', return_value=mock_pd):
        with pytest.raises(ValueError) as exc_info:
            result_to_df([
                {"@id": "test1", "@type": "Type1"},
                {"@id": "test2", "@type": "Type2"}
            ])
        
        assert "multiple type" in str(exc_info.value).lower()


def test_result_to_df_class_not_in_schema():
    """Test that result_to_df raises InterfaceError when class not found in schema."""
    mock_pd = MagicMock()
    mock_client = MagicMock()
    
    # Setup mock DataFrame
    mock_df = MagicMock()
    mock_df.__getitem__.return_value.unique.return_value = ["UnknownClass"]
    mock_df.columns = ["@id", "@type"]
    mock_df.rename.return_value = mock_df
    mock_df.drop.return_value = mock_df
    
    mock_pd.DataFrame.return_value.from_records.return_value = mock_df
    mock_client.get_existing_classes.return_value = {"KnownClass": {}}
    mock_client.db = "testdb"
    
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module', return_value=mock_pd):
        with pytest.raises(InterfaceError) as exc_info:
            result_to_df(
                [{"@id": "test1", "@type": "UnknownClass"}],
                max_embed_dep=1,
                client=mock_client
            )
        
        assert "UnknownClass" in str(exc_info.value)
        assert "not found" in str(exc_info.value)


def test_result_to_df_basic_conversion():
    """Test basic result_to_df conversion without embedding."""
    mock_pd = MagicMock()
    
    # Setup mock DataFrame
    mock_df = MagicMock()
    mock_df.__getitem__.return_value.unique.return_value = ["Person"]
    mock_df.columns = ["@id", "@type", "name"]
    mock_df.rename.return_value = mock_df
    mock_df.drop.return_value = mock_df
    
    mock_pd.DataFrame.return_value.from_records.return_value = mock_df
    
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module', return_value=mock_pd):
        result = result_to_df([
            {"@id": "Person/Jane", "@type": "Person", "name": "Jane"}
        ])
        
        # Should return the DataFrame
        assert result is not None


def test_result_to_df_with_keepid():
    """Test result_to_df with keepid=True."""
    mock_pd = MagicMock()
    
    # Setup mock DataFrame
    mock_df = MagicMock()
    mock_df.__getitem__.return_value.unique.return_value = ["Person"]
    mock_df.columns = ["@id", "@type", "name"]
    
    mock_pd.DataFrame.return_value.from_records.return_value = mock_df
    
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module', return_value=mock_pd):
        result = result_to_df([
            {"@id": "Person/Jane", "@type": "Person", "name": "Jane"}
        ], keepid=True)
        
        # Should return the DataFrame
        assert result is not None
        # Should not call rename when keepid=True
        mock_df.rename.assert_not_called()


def test_result_to_df_requires_client_for_embedding():
    """Test that result_to_df requires client when max_embed_dep > 0."""
    mock_pd = MagicMock()
    
    # Setup basic mock
    mock_df = MagicMock()
    mock_df.__getitem__.return_value.unique.return_value = ["Person"]
    mock_pd.DataFrame.return_value.from_records.return_value = mock_df
    
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module', return_value=mock_pd):
        # This tests the ValueError raised at line 18-21
        with pytest.raises(ValueError) as exc_info:
            result_to_df(
                [{"@id": "Person/Jane", "@type": "Person"}],
                max_embed_dep=2,  # Requires client
                client=None  # But no client provided
            )
        
        assert "client need to be provide" in str(exc_info.value)


def test_result_to_df_expand_nested_json():
    """Test that result_to_df expands nested JSON structures."""
    mock_pd = MagicMock()
    
    # Setup mock DataFrame with nested structure
    mock_df = MagicMock()
    mock_df.__getitem__.return_value.unique.return_value = ["Person"]
    mock_df.columns = ["Document id", "address"]
    mock_df.rename.return_value = mock_df
    mock_df.drop.return_value = mock_df
    mock_df.join.return_value = mock_df
    
    # Mock json_normalize to simulate expansion
    mock_expanded = MagicMock()
    mock_expanded.columns = ["@id", "street"]
    mock_pd.json_normalize.return_value = mock_expanded
    
    mock_pd.DataFrame.return_value.from_records.return_value = mock_df
    
    with patch('terminusdb_client.woqldataframe.woqlDataframe.import_module', return_value=mock_pd):
        result = result_to_df([
            {
                "@id": "Person/Jane",
                "@type": "Person",
                "address": {"@id": "Address/1", "street": "Main St"}
            }
        ])
        
        # json_normalize should be called for expansion
        assert mock_pd.json_normalize.called
        assert result is not None
