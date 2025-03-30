from typing import Iterator
from click import Command, Group
from evn.cli.cli_registry import CliRegistry
from evn.cli.cli_metaclass import CliBase

def walk_commands(root: type[CliBase], seenit = None) -> Iterator[tuple[str, Command]]:
    if seenit is None: seenit = set()
    if root in seenit: return
    seenit.add(root)
    group = getattr(root, "__group__", None)
    assert group is not None and isinstance(group, Group)
    base_path = f'{root.get_command_path()}'
    for name, cmd in group.commands.items():
        # Check if this command is itself a group associated with a registered CLI class
        if isinstance(cmd, Group):
            for cls in CliRegistry.all_cli_classes():
                if getattr(cls, "__group__", None) is cmd:
                    yield from walk_commands(cls, seenit)
                    break
        else:
            full_path = f"{base_path}.{name}"
            yield full_path, cmd


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
    seenit = set()
    for cls in CliRegistry.all_cli_classes():
        paths.extend([p for p, _ in walk_commands(cls, seenit)])
    return paths
