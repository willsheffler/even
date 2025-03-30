from click import Command
from evn.cli.cli_command_resolver import walk_commands, find_command, get_all_cli_paths
from evn.cli.cli_metaclass import CliBase


# Dummy classes for test
class CLITestSub(CliBase):
    def hello(self, name: str):
        print(f"Hello {name}")


class CLITestTop(CliBase):
    def greet(self, name: str):
        print(f"Hi {name}")

    sub = CLITestSub()


def test_walk_commands_finds_all():
    top_paths = [p for p, _ in walk_commands(CLITestTop)]
    assert "greet" in top_paths
    assert "sub" in top_paths
    assert "sub.hello" in top_paths


def test_find_command_by_path():
    cmd = find_command(CLITestTop, "sub")
    assert isinstance(cmd, Command)
    sub_cmd = find_command(CLITestTop, "sub.hello")
    assert isinstance(sub_cmd, Command)


def test_get_all_cli_paths_contains_expected():
    paths = get_all_cli_paths()
    assert any("greet" in p for p in paths)
    assert any("sub.hello" in p for p in paths)
