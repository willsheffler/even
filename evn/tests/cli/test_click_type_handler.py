# evn/tests/cli/test_click_type_handler.py
import pytest
import click
from evn.cli.click_type_handler import ClickTypeHandler, MetadataPolicy, get_cached_paramtype

# Dummy handler classes for testing. Mark them as not tests.
class DummyIntHandler(ClickTypeHandler):
    __test__ = False  # Prevent pytest collection.
    supported_types = {int: 'metadata_required'}
    _priority_bonus = 5

    def convert(self, value, param, ctx):
        try:
            preprocessed = self.preprocess_value(value)
            converted = int(preprocessed)
            return self.postprocess_value(converted)
        except Exception as e:
            self.fail(f"DummyIntHandler conversion failed: {e}", param, ctx)

class DummyBoolHandler(ClickTypeHandler):
    __test__ = False
    supported_types = {bool: 'metadata_required'}
    _priority_bonus = 2

    def convert(self, value, param, ctx):
        val = self.preprocess_value(value)
        if isinstance(val, str) and val.lower() in ['true', '1', 'yes']:
            return True
        elif isinstance(val, str) and val.lower() in ['false', '0', 'no']:
            return False
        else:
            self.fail(f"DummyBoolHandler conversion failed for {value}", param, ctx)

class DummyListHandler(ClickTypeHandler):
    __test__ = False
    # For list types, we require metadata to specify the element type.
    supported_types = {list: MetadataPolicy.REQUIRED}
    _priority_bonus = 3

    def convert(self, value, param, ctx):
        raw_list = self.preprocess_value(value)
        if not isinstance(raw_list, str):
            self.fail("Expected a string for list conversion", param, ctx)
        items = [item.strip() for item in raw_list.split(',')]
        try:
            # Use metadata to determine the element type; assume metadata is stored as self.metadata.
            element_type = self.metadata_element_type  # Will be set in preprocess_value.
        except AttributeError:
            self.fail("Missing element type metadata", param, ctx)
        try:
            converted = [element_type(item) for item in items]
            return self.postprocess_value(converted)
        except Exception as e:
            self.fail(f"List conversion failed: {e}", param, ctx)

    def preprocess_value(self, raw: str):
        # For testing, we expect metadata to be passed via an attribute.
        self.metadata_element_type = self.metadata if hasattr(self, 'metadata') else int
        return raw

# New Dummy handler for float.
class DummyFloatHandler(ClickTypeHandler):
    __test__ = False
    supported_types = {float: 'metadata_required'}
    _priority_bonus = 4

    def convert(self, value, param, ctx):
        try:
            preprocessed = self.preprocess_value(value)
            converted = float(preprocessed)
            return self.postprocess_value(converted)
        except Exception as e:
            self.fail(f"DummyFloatHandler conversion failed: {e}", param, ctx)

# New Dummy handler for string.
class DummyStringHandler(ClickTypeHandler):
    __test__ = False
    supported_types = {str: 'metadata_required'}
    _priority_bonus = 1

    def convert(self, value, param, ctx):
        try:
            preprocessed = self.preprocess_value(value)
            return self.postprocess_value(preprocessed)
        except Exception as e:
            self.fail(f"DummyStringHandler conversion failed: {e}", param, ctx)

# Tests for handles_type method.
def test_handles_type_int():
    handler = DummyIntHandler()
    assert handler.handles_type(int) is True
    assert handler.handles_type(str) is False

def test_handles_type_bool():
    handler = DummyBoolHandler()
    assert handler.handles_type(bool) is True
    assert handler.handles_type(int) is False

def test_handles_type_list_with_metadata():
    handler = DummyListHandler()
    assert handler.handles_type(list, metadata=int) is True
    assert handler.handles_type(list, metadata=None) is False

def test_handles_type_float():
    handler = DummyFloatHandler()
    assert handler.handles_type(float) is True
    assert handler.handles_type(int) is False

def test_handles_type_string():
    handler = DummyStringHandler()
    assert handler.handles_type(str) is True
    assert handler.handles_type(int) is False

# # Tests for compute_priority
# def test_compute_priority():
#     handler = DummyIntHandler()
#     priority = handler.compute_priority(int, None, 1)
#     # Expected: mro_rank (1) + _priority_bonus (5) + specificity (0) = 6
#     assert priority == 6

# def test_compute_priority_with_metadata():
#     handler = DummyListHandler()
#     priority = handler.compute_priority(list, int, 2)
#     # Expected: 2 + _priority_bonus (3) + METADATA_BONUS (10) + specificity (0) = 15
#     assert priority == 15

# Test caching of paramtype
def test_get_cached_paramtype():
    pt1 = get_cached_paramtype(DummyIntHandler, int, None)
    pt2 = get_cached_paramtype(DummyIntHandler, int, None)
    assert pt1 is pt2

# Test conversion: DummyIntHandler should convert a string to int.
def test_convert_int():
    handler = DummyIntHandler()
    class DummyParam:
        pass
    ctx = click.get_current_context(silent=True)
    result = handler.convert("123", DummyParam(), ctx)
    assert result == 123

# Test conversion: DummyBoolHandler should convert strings to booleans.
def test_convert_bool_true():
    handler = DummyBoolHandler()
    class DummyParam:
        pass
    ctx = click.get_current_context(silent=True)
    result = handler.convert("yes", DummyParam(), ctx)
    assert result is True

def test_convert_bool_false():
    handler = DummyBoolHandler()
    class DummyParam:
        pass
    ctx = click.get_current_context(silent=True)
    result = handler.convert("no", DummyParam(), ctx)
    assert result is False

# Test conversion for list: Using DummyListHandler.
def test_convert_list():
    handler = DummyListHandler()
    handler.metadata = int  # Simulate metadata.
    class DummyParam:
        pass
    ctx = click.get_current_context(silent=True)
    result = handler.convert("1, 2, 3", DummyParam(), ctx)
    assert result == [1, 2, 3]

# Test conversion: DummyFloatHandler should convert a string to float.
def test_convert_float():
    handler = DummyFloatHandler()
    class DummyParam:
        pass
    ctx = click.get_current_context(silent=True)
    result = handler.convert("123.45", DummyParam(), ctx)
    assert result == 123.45

# Test conversion: DummyStringHandler should return the input string.
def test_convert_string():
    handler = DummyStringHandler()
    class DummyParam:
        pass
    ctx = click.get_current_context(silent=True)
    result = handler.convert("hello world", DummyParam(), ctx)
    assert result == "hello world"

if __name__ == "__main__":
    pytest.main([__file__])
