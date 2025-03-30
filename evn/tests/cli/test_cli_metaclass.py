# evn/tests/cli/test_cli_metaclass.py
import pytest
import click
from click.testing import CliRunner
from evn.cli.cli_metaclass import CliBase, CliMeta
from evn.cli.auto_click_decorator import auto_click_decorate_command
from evn.cli.cli_logger import CliLogger
from evn.cli.click_type_handler import ClickTypeHandlers

# Define a dummy parent CLI tool.
class CLIParent(CliBase):
    click_type_handlers = []  # For testing, no extra handlers needed.

    @classmethod
    def _config(cls):
        return {"parent_option": "value_from_parent"}

    def greet(self, name: str):
        """Command that greets a person."""
        click.echo(f"Hello, {name}!")

# Define a dummy child CLI tool.
class CLIChild(CLIParent):
    click_type_handlers = []  # Inherit parent's handlers.

    @classmethod
    def _config(cls):
        return {"child_option": "value_from_child"}

    def farewell(self, name: str):
        """Command that says goodbye."""
        click.echo(f"Goodbye, {name}!")

def test_singleton_behavior():
    parent1 = CLIParent()
    parent2 = CLIParent()
    assert parent1 is parent2

def test_parent_command_registration():
    runner = CliRunner()
    # CLIParent's group should include the "greet" command.
    result = runner.invoke(CLIParent.__group__, ["greet", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output

def test_child_command_registration():
    runner = CliRunner()
    # CLIChild's group is attached as a subcommand of CLIParent's group.
    # Invoke as: parent group "child" then command "farewell".
    result = runner.invoke(CLIParent.__group__, ["child", "farewell", "Bob"])
    assert result.exit_code == 0
    assert "Goodbye, Bob!" in result.output

def test_config_logging():
    parent_instance = CLIParent()
    assert hasattr(CLIParent, "__config__")
    assert CLIParent.__config__ == {"parent_option": "value_from_parent"}
    logs = CliLogger.get_log(CLIParent)
    found = any("Configuration applied" in log.get("message", "") for log in logs)
    assert found

def test_instance_logging():
    parent_instance = CLIParent()
    logs = CliLogger.get_log(CLIParent)
    found = any("Instance created" in log.get("message", "") for log in logs)
    assert found

def test_get_full_path():
    parent_instance = CLIParent()
    child_instance = CLIChild()
    assert parent_instance.get_full_path() == "CLIParent"
    assert child_instance.get_full_path() == "CLIParent.CLIChild"

def test_greet_command():
    runner = CliRunner()
    result = runner.invoke(CLIParent.__group__, ["greet", "Alice"])

def test_greet_command_exists():
    assert "greet" in CLIParent.__group__.commands

class CLIDebugTest(CliBase):

    def greet(self, name: str, default=7):
        """Basic test for argument passing."""
        click.echo(f"Hello, {name}!")

def test_debug_sanity_command_runs():
    runner = CliRunner()
    result = runner.invoke(CLIDebugTest.__group__, ["greet", "TestUser"])
    assert result.exit_code == 0
    assert "Hello, TestUser!" in result.output

def test_click_metadata_capture():
    decorated = auto_click_decorate_command(CLIDebugTest.greet, ClickTypeHandlers)
    assert [['--default'],['name']] == [p.opts for p in getattr(decorated, '__click_params__', [])]
    assert {} == getattr(decorated, '__click_attrs__', {})

def test_empty_cli_group_creates_successfully():
    class EmptyCLI(metaclass=CliMeta):
        pass

    assert isinstance(EmptyCLI.__group__, click.Group)
    assert len(EmptyCLI.__group__.commands) == 0

def test_config_is_applied():
    class ConfiguredCLI(metaclass=CliMeta):
        @classmethod
        def _config(cls):
            return {"hello": "world"}

    assert ConfiguredCLI.__config__ == {"hello": "world"}

def test_command_override():
    class BaseCLI(metaclass=CliMeta):
        def greet(self):
            print("base")

    class SubCLI(BaseCLI):
        def greet(self):
            print("sub")

    runner = CliRunner()
    result = runner.invoke(SubCLI.__group__, ['greet'])
    assert "base" not in result.output
    assert "sub" in result.output


if __name__ == "__main__":
    pytest.main([__file__])
