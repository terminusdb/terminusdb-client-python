"""Tests for woql_utils.py module."""
import json
from datetime import datetime
from unittest.mock import Mock
import pytest

from terminusdb_client.woql_utils import (
    _result2stream,
    _args_as_payload,
    _finish_response,
    _clean_list,
    _clean_dict,
    _dt_list,
    _dt_dict
)
from terminusdb_client.errors import DatabaseError


def test_result2stream_basic():
    """Test _result2stream with basic JSON objects."""
    result = '{"a": 1}{"b": 2}'
    stream = list(_result2stream(result))
    
    assert len(stream) == 2
    assert stream[0] == {"a": 1}
    assert stream[1] == {"b": 2}


def test_result2stream_with_whitespace():
    """Test _result2stream handles whitespace between objects."""
    result = '{"a": 1}  \n  {"b": 2}'
    stream = list(_result2stream(result))
    
    assert len(stream) == 2
    assert stream[0] == {"a": 1}
    assert stream[1] == {"b": 2}


def test_result2stream_empty():
    """Test _result2stream with empty string."""
    result = ''
    stream = list(_result2stream(result))
    
    assert len(stream) == 0


def test_args_as_payload_filters_none():
    """Test _args_as_payload filters out None values."""
    args = {"a": 1, "b": None, "c": "test"}
    result = _args_as_payload(args)
    
    assert result == {"a": 1, "c": "test"}
    assert "b" not in result


def test_args_as_payload_filters_falsy():
    """Test _args_as_payload filters out falsy values."""
    args = {"a": 1, "b": 0, "c": "", "d": False, "e": "test"}
    result = _args_as_payload(args)
    
    # Only truthy values remain
    assert result == {"a": 1, "e": "test"}


def test_finish_response_success():
    """Test _finish_response with 200 status."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "success"
    
    result = _finish_response(mock_response)
    
    assert result == "success"


def test_finish_response_with_version():
    """Test _finish_response returns version header."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "data"
    mock_response.headers = {"Terminusdb-Data-Version": "v1.0"}
    
    text, version = _finish_response(mock_response, get_version=True)
    
    assert text == "data"
    assert version == "v1.0"


def test_finish_response_streaming():
    """Test _finish_response with streaming=True."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = iter(["line1", "line2"])
    
    result = _finish_response(mock_response, streaming=True)
    
    # Should return iterator
    lines = list(result)
    assert lines == ["line1", "line2"]
    mock_response.iter_lines.assert_called_once()


def test_finish_response_error():
    """Test _finish_response raises DatabaseError on error status."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "error"
    mock_response.headers = {"content-type": "text/plain"}
    
    with pytest.raises(DatabaseError):
        _finish_response(mock_response)


def test_clean_list_with_datetime():
    """Test _clean_list converts datetime to isoformat."""
    dt = datetime(2025, 1, 1, 12, 0, 0)
    obj = [dt, "string", 123]
    
    result = _clean_list(obj)
    
    assert result[0] == dt.isoformat()
    assert result[1] == "string"
    assert result[2] == 123


def test_clean_list_nested():
    """Test _clean_list with nested structures."""
    dt = datetime(2025, 1, 1)
    obj = [
        "string",
        {"key": dt},
        [1, 2, dt]
    ]
    
    result = _clean_list(obj)
    
    assert result[0] == "string"
    assert result[1] == {"key": dt.isoformat()}
    assert result[2] == [1, 2, dt.isoformat()]


def test_clean_dict_with_datetime():
    """Test _clean_dict converts datetime to isoformat."""
    dt = datetime(2025, 1, 1, 12, 0, 0)
    obj = {
        "date": dt,
        "name": "test",
        "count": 42
    }
    
    result = _clean_dict(obj)
    
    assert result["date"] == dt.isoformat()
    assert result["name"] == "test"
    assert result["count"] == 42


def test_clean_dict_nested():
    """Test _clean_dict with nested structures."""
    dt = datetime(2025, 1, 1)
    obj = {
        "name": "test",
        "nested": {"date": dt},
        "list": [1, dt, "string"]
    }
    
    result = _clean_dict(obj)
    
    assert result["name"] == "test"
    assert result["nested"] == {"date": dt.isoformat()}
    assert result["list"] == [1, dt.isoformat(), "string"]


def test_clean_dict_with_iterable():
    """Test _clean_dict handles iterables correctly."""
    obj = {
        "tuple": (1, 2, 3),
        "list": [4, 5, 6]
    }
    
    result = _clean_dict(obj)
    
    assert result["tuple"] == [1, 2, 3]
    assert result["list"] == [4, 5, 6]


def test_dt_list_parses_isoformat():
    """Test _dt_list converts ISO format strings to datetime."""
    obj = ["2025-01-01T12:00:00", "not a date", 123]
    
    result = _dt_list(obj)
    
    assert isinstance(result[0], datetime)
    assert result[0] == datetime(2025, 1, 1, 12, 0, 0)
    assert result[1] == "not a date"
    assert result[2] == 123


def test_dt_list_nested():
    """Test _dt_list with nested structures."""
    obj = [
        "2025-01-01",
        {"date": "2025-01-01T10:00:00"},
        ["2025-01-01", "text"]
    ]
    
    result = _dt_list(obj)
    
    assert isinstance(result[0], datetime)
    # Note: _dt_list calls _clean_dict on nested dicts, not _dt_dict
    # So dates in nested dicts are not parsed
    assert result[1] == {"date": "2025-01-01T10:00:00"}
    # Note: _dt_list calls _clean_list on nested lists, not _dt_list
    # So dates in nested lists are not parsed
    assert result[2] == ["2025-01-01", "text"]


def test_dt_dict_parses_isoformat():
    """Test _dt_dict converts ISO format strings to datetime."""
    obj = {
        "created": "2025-01-01T12:00:00",
        "name": "test",
        "invalid": "not a date"
    }
    
    result = _dt_dict(obj)
    
    assert isinstance(result["created"], datetime)
    assert result["created"] == datetime(2025, 1, 1, 12, 0, 0)
    assert result["name"] == "test"
    assert result["invalid"] == "not a date"


def test_dt_dict_nested():
    """Test _dt_dict with nested structures."""
    obj = {
        "name": "test",
        "nested": {"date": "2025-01-01"},
        "list": ["2025-01-01T10:00:00", 123]
    }
    
    result = _dt_dict(obj)
    
    assert result["name"] == "test"
    assert isinstance(result["nested"]["date"], datetime)
    assert isinstance(result["list"][0], datetime)
    assert result["list"][1] == 123


def test_dt_dict_with_iterable():
    """Test _dt_dict handles iterables with dates."""
    obj = {
        "dates": ["2025-01-01", "2025-01-02"],
        "mixed": ["2025-01-01", "text", 123]
    }
    
    result = _dt_dict(obj)
    
    assert isinstance(result["dates"][0], datetime)
    assert isinstance(result["dates"][1], datetime)
    assert isinstance(result["mixed"][0], datetime)
    assert result["mixed"][1] == "text"


def test_clean_list_handles_dict_items():
    """Test _clean_list correctly identifies objects with items() method."""
    dt = datetime(2025, 1, 1)
    obj = [
        {"key1": "value1"},
        {"key2": dt}
    ]
    
    result = _clean_list(obj)
    
    assert result[0] == {"key1": "value1"}
    assert result[1] == {"key2": dt.isoformat()}


def test_dt_list_handles_dict_items():
    """Test _dt_list correctly processes nested dicts."""
    obj = [
        {"date": "2025-01-01"},
        {"name": "test"}
    ]
    
    result = _dt_list(obj)
    
    # _dt_list calls _clean_dict on dict items
    assert result[0] == {"date": "2025-01-01"}
    assert result[1] == {"name": "test"}
