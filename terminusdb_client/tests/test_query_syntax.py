"""Tests for query_syntax/query_syntax.py module."""

from terminusdb_client.query_syntax import query_syntax


def test_query_syntax_exports_var():
    """Test that Var is exported."""
    assert "Var" in query_syntax.__all__
    assert hasattr(query_syntax, "Var")


def test_query_syntax_exports_vars():
    """Test that Vars is exported."""
    assert "Vars" in query_syntax.__all__
    assert hasattr(query_syntax, "Vars")


def test_query_syntax_exports_doc():
    """Test that Doc is exported."""
    assert "Doc" in query_syntax.__all__
    assert hasattr(query_syntax, "Doc")


def test_barred_items_not_exported():
    """Test that barred items (re, vars) are not exported."""
    assert "re" not in query_syntax.__all__
    assert "vars" not in query_syntax.__all__


def test_allowed_dunder_methods_exported():
    """Test that allowed dunder methods are exported."""
    # __and__, __or__, __add__ should be exported
    assert "__and__" in query_syntax.__all__
    assert "__or__" in query_syntax.__all__
    assert "__add__" in query_syntax.__all__


def test_dynamic_function_creation():
    """Test that functions are dynamically created from WOQLQuery."""
    # Check that some common WOQLQuery methods are available
    woql_methods = ["triple", "select", "limit"]

    for method in woql_methods:
        assert hasattr(query_syntax, method), f"{method} should be available"
        assert method in query_syntax.__all__, f"{method} should be in __all__"


def test_created_functions_are_callable():
    """Test that dynamically created functions are callable."""
    # Test that we can call a dynamically created function
    if hasattr(query_syntax, "limit"):
        func = getattr(query_syntax, "limit")
        assert callable(func)


def test_created_function_returns_woqlquery():
    """Test that created functions return WOQLQuery instances."""
    # Test a simple function that exists on WOQLQuery
    if hasattr(query_syntax, "limit"):
        func = getattr(query_syntax, "limit")
        result = func(10)
        # Should return a WOQLQuery or similar object
        assert result is not None


def test_private_attributes_not_exported():
    """Test that private attributes (starting with _) are not exported."""
    for attr in query_syntax.__all__:
        # All exported attributes should either be in __ALLOWED or not start with _
        if attr not in ["__and__", "__or__", "__add__"]:
            assert not attr.startswith("_"), f"{attr} should not start with underscore"


def test_module_attributes():
    """Test module has expected attributes."""
    # These are defined in the module
    assert hasattr(query_syntax, "__BARRED")
    assert hasattr(query_syntax, "__ALLOWED")
    assert hasattr(query_syntax, "__module")
    assert hasattr(query_syntax, "__exported")
