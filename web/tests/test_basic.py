"""Basic tests for StellarTracker"""

def test_basic():
    """Basic test that always passes"""
    assert True

def test_imports():
    """Test that we can import Flask"""
    try:
        import flask
        assert flask is not None
    except ImportError:
        assert False, "Flask not installed"
