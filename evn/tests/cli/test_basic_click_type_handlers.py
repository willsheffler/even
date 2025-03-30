# test_basic_click_type_handlers.py
import pytest
import click
import uuid
import datetime
from evn.cli.basic_click_type_handlers import (
    BasicStringHandler,
    BasicIntHandler,
    BasicFloatHandler,
    BasicBoolHandler,
    BasicUUIDHandler,
    BasicFileHandler,
    BasicPathHandler,
    BasicChoiceHandler,
    BasicIntRangeHandler,
    BasicFloatRangeHandler,
    BasicDateTimeHandler,
)

# Dummy parameter for testing.
class DummyParam:
    pass

# Use Click's context.
ctx = click.get_current_context(silent=True)

def test_basic_string_handler():
    handler = BasicStringHandler()
    result = handler.convert("hello", DummyParam(), ctx)
    assert result == "hello"

def test_basic_int_handler():
    handler = BasicIntHandler()
    result = handler.convert("42", DummyParam(), ctx)
    assert result == 42

def test_basic_float_handler():
    handler = BasicFloatHandler()
    result = handler.convert("3.1415", DummyParam(), ctx)
    assert result == pytest.approx(3.1415)

def test_basic_bool_handler_true():
    handler = BasicBoolHandler()
    result = handler.convert("yes", DummyParam(), ctx)
    assert result is True

def test_basic_bool_handler_false():
    handler = BasicBoolHandler()
    result = handler.convert("no", DummyParam(), ctx)
    assert result is False

def test_basic_uuid_handler():
    u = uuid.uuid4()
    handler = BasicUUIDHandler()
    result = handler.convert(str(u), DummyParam(), ctx)
    assert result == u

def test_basic_file_handler(tmp_path):
    # Create a temporary file with known content.
    temp_file = tmp_path / "test.txt"
    temp_file.write_text("file content")
    handler = BasicFileHandler()
    result = handler.convert(str(temp_file), DummyParam(), ctx)
    # The result should be an open file.
    content = result.read()
    result.close()
    assert content == "file content"

def test_basic_path_handler(tmp_path):
    handler = BasicPathHandler()
    result = handler.convert(str(tmp_path), DummyParam(), ctx)
    # click.Path returns a string by default.
    assert isinstance(result, str)
    # Optionally, ensure the result equals the input path.
    assert result == str(tmp_path)

def test_basic_choice_handler():
    handler = BasicChoiceHandler()
    handler.choices = ["apple", "banana", "cherry"]
    result = handler.convert("banana", DummyParam(), ctx)
    assert result == "banana"
    with pytest.raises(click.BadParameter):
        handler.convert("durian", DummyParam(), ctx)

def test_basic_int_range_handler():
    handler = BasicIntRangeHandler()
    handler.min = 10
    handler.max = 20
    result = handler.convert("15", DummyParam(), ctx)
    assert result == 15
    with pytest.raises(click.BadParameter):
        handler.convert("5", DummyParam(), ctx)

def test_basic_float_range_handler():
    handler = BasicFloatRangeHandler()
    handler.min = 1.0
    handler.max = 2.0
    result = handler.convert("1.5", DummyParam(), ctx)
    assert result == pytest.approx(1.5)
    with pytest.raises(click.BadParameter):
        handler.convert("0.5", DummyParam(), ctx)

def test_basic_datetime_handler():
    handler = BasicDateTimeHandler()
    handler.formats = ("%Y-%m-%d", )
    date_str = "2023-01-01"
    result = handler.convert(date_str, DummyParam(), ctx)
    expected = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    assert result == expected

if __name__ == "__main__":
    pytest.main([__file__])
