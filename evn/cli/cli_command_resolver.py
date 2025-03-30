from typing import Iterator
from click import Command, Group
from evn.cli.cli_registry import CliRegistry
from evn.cli.cli_metaclass import CliBase


def walk_commands(
    root: type[CliBase], prefix: str = "", visited: set[type] = None
) -> Iterator[tuple[str, Command]]:
    if visited is None:
        visited = set()

    if root in visited:
        return
    visited.add(root)

    group = getattr(root, "__group__", None)
    if group is None or not isinstance(group, Group):
        return

    base_path = prefix or group.name

    for name, cmd in group.commands.items():
        full_path = f"{base_path}.{name}" if prefix else name
        yield full_path, cmd

        # Check if this command is itself a group associated with a registered CLI class
        if isinstance(cmd, Group):
            for cls in CliRegistry.all_cli_classes():
                if getattr(cls, "__group__", None) is cmd:
                    yield from walk_commands(cls, full_path, visited)
                    break


def find_command(root: type[CliBase], path: str) -> Command:
    parts = path.split(".")
    current = root.__group__
    for part in parts:
        if not isinstance(current, Group) or part not in current.commands:
            raise KeyError(f"Command path not found: {path}")
        current = current.commands[part]
    return current


def get_all_cli_paths() -> list[str]:
    paths = []
    for cls in CliRegistry.all_cli_classes():
        if not hasattr(cls, "__parent__"):
            paths.extend(p for p, _ in walk_commands(cls))
    return paths
