# evn/tests/cli/test_auto_click_decorator.py
import pytest
import click
import typing
from click.testing import CliRunner
from evn.cli.auto_click_decorator import auto_click_decorate_command

# Import default basic handlers from our basic conversion layer.
from evn.cli.basic_click_type_handlers import BasicIntHandler, BasicStringHandler, BasicBoolHandler

# Prepare a list of type handlers.
TYPE_HANDLERS = [BasicIntHandler, BasicStringHandler, BasicBoolHandler]

# Dummy command with no manual decorators; use click.echo to print output.
def dummy_command(a: int, b: str, c: bool = False):
    """Dummy command for testing auto-decoration."""
    click.echo(f"{a}-{b}-{c}")

# Auto-decorate the function.
auto_dummy_command = auto_click_decorate_command(dummy_command, TYPE_HANDLERS)
# Now wrap it with click.command.
auto_dummy_command = click.command()(auto_dummy_command)

# Define a function with a manual option for parameter b.
def partial_manual(a: int, b: str):
    """Partial manual command for testing merging."""
    click.echo(f"{a}-{b}")
# Manually decorate parameter b.
partial_manual = click.option("--b", type=str, default="manual")(partial_manual)
auto_partial_manual = auto_click_decorate_command(partial_manual, TYPE_HANDLERS)
auto_partial_manual = click.command()(auto_partial_manual)

# Test using Annotated for parameter.
def annotated_command(a: typing.Annotated[int, "metadata info"], b: str):
    """Command with Annotated parameter."""
    click.echo(f"{a}-{b}")
auto_annotated_command = auto_click_decorate_command(annotated_command, TYPE_HANDLERS)
auto_annotated_command = click.command()(auto_annotated_command)

# Test with an internal parameter that should be skipped (and supplied as None).
def internal_param_command(a: int, _internal: str, b: str):
    """Command that has an internal parameter (_internal) that should be ignored."""
    # _internal should be supplied as None.
    click.echo(f"{a}-{_internal}-{b}")
auto_internal_command = auto_click_decorate_command(internal_param_command, TYPE_HANDLERS)
auto_internal_command = click.command()(auto_internal_command)

# Test with multiple parameters and defaults.
def complex_command(a: int, b: str = "default", c: bool = False, d: float = 3.14):
    """A command with mixed required and optional parameters."""
    click.echo(f"{a}-{b}-{c}-{d}")
auto_complex_command = auto_click_decorate_command(complex_command, TYPE_HANDLERS)
auto_complex_command = click.command()(auto_complex_command)

def test_auto_generated_parameters():
    runner = CliRunner()
    # 'a' and 'b' are required, 'c' is an optional boolean flag.
    result = runner.invoke(auto_dummy_command, ["123", "hello", "--c"])
    assert result.exit_code == 0
    # The output should be "123-hello-True"
    assert "123-hello-True" in result.output

def test_manual_decorator_merging():
    runner = CliRunner()
    result = runner.invoke(auto_partial_manual, ["789", "--b", "manual_override"])
    assert result.exit_code == 0
    # Expect the output to reflect the manual override.
    assert "789-manual_override" in result.output

def test_annotated_parameter():
    runner = CliRunner()
    # Even though we use Annotated for parameter a, it should be processed as int.
    result = runner.invoke(auto_annotated_command, ["321", "world"])
    assert result.exit_code == 0
    assert "321-world" in result.output

def test_internal_parameter_skipped():
    runner = CliRunner()
    # _internal is not exposed; only provide values for a and b.
    result = runner.invoke(auto_internal_command, ["111", "visible"])
    assert result.exit_code == 0
    # The output should show that _internal is None.
    assert "111-None-visible" in result.output

def test_complex_command_defaults():
    runner = CliRunner()
    # Only a is required; others should use defaults.
    result = runner.invoke(auto_complex_command, ["555"])
    assert result.exit_code == 0
    # Expected output: "555-default-False-3.14"
    assert "555-default-False-3.14" in result.output

def test_error_on_manual_click_command():
    # Define a function already wrapped with click.command.
    @click.command()
    def already_command(x: int):
        click.echo(str(x))
    with pytest.raises(RuntimeError):
        auto_click_decorate_command(already_command, TYPE_HANDLERS)

if __name__ == "__main__":
    pytest.main([__file__])
