"""
cli_metaclass.py

This module defines the `CliMeta` metaclass, which automatically turns classes into Click-based CLI command groups.
It forms the backbone of the EVeN CLI system, enabling command registration via inheritance and minimal boilerplate.

The key behaviors of this metaclass include:

- Creating a `click.Group` for each CLI class.
- Registering the group with a parent group (if inherited).
- Registering each public method as a Click command via `auto_click_decorate_command`.
- Injecting a structured logging method using `CliLogger`.
- Composing type handlers from `ClickTypeHandlers`.

Each CLI class using `CliMeta` gains the following attributes:
- `__group__`: a `click.Group` containing its registered commands.
- `__parent__`: a reference to its parent CLI class (if any).
- `__type_handlers__`: merged parameter conversion handlers.
- `__config__`: optional config returned from `_config()` classmethod.
- `_log`: a callable logger that delegates to `CliLogger`.

Usage Example:

    >>> class ProjectCLI(CLI):
    ...     def create(self, name: str):
    ...         print(f"Creating project {name}")
    >>> from click.testing import CliRunner
    >>> cli = ProjectCLI.__group__
    >>> runner = CliRunner()
    >>> result = runner.invoke(cli, ['create', 'demo'])
    >>> assert "Creating project demo" in result.output

Dependencies:
- click
- evn.cli.auto_click_decorator
- evn.cli.cli_logger
- evn.cli.cli_registry
- evn.cli.click_type_handler

See Also:
- test_cli_metaclass.py — for validated examples and coverage.
"""

import click
import datetime
import functools
import typing
from evn.cli.auto_click_decorator import auto_click_decorate_command
from evn.cli.cli_registry import CliRegistry
from evn.cli.cli_logger import CliLogger
from evn.cli.click_type_handler import ClickTypeHandlers

def cls_to_groupname(cls):
    """
    Converts a class name to a Click group name.
    This is typically the same as the class name but can be customized if needed.

    Args:
        cls (type): The class to convert.

    Returns:
        str: The name to be used for the Click group.
    """
    if cls.__name__ == 'CLI': return '<exe>'
    return cls.__name__.lower().removeprefix('cli').removesuffix('cli')

class CliMeta(type):
    # there are NOT ACTUALLY USED just to make the type checker happy
    __group__: click.Group
    __parent__: 'CLI | None'
    __type_handlers__: ClickTypeHandlers
    __all_type_handlers__: list[ClickTypeHandlers]
    __config__: dict
    _config: classmethod
    _log: typing.Callable[['dict|str'], None]

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        @classmethod
        def log(cls, *a, **kw):
            CliLogger.log(cls, *a, **kw)

        cls._log, cls.__log__ = log, []

        cls.__group__ = click.Group(name=cls_to_groupname(cls))
        CliLogger.log(cls, f"Registered group: {cls.__group__.name}", event="group_registered")
        # print(f"[CliMeta] Registered group for {cls.__name__} -> {cls.__group__.name}")

        cls.__parent__ = None
        for base in bases:
            assert hasattr(base, "__group__")
            assert not cls.__parent__
            cls.__parent__ = base
            base.__group__.add_command(cls.__group__, name=cls.__group__.name)

        cls.__all_type_handlers__ = []
        for base in cls.__mro__:
            handlers = ClickTypeHandlers(getattr(base, '__type_handlers__', {}))
            cls.__all_type_handlers__.append(handlers)

        for name in cls.__dict__:
            if cls.__name__ == 'CLI': break
            if name.startswith("_"): continue
            method = getattr(cls, name)
            if not callable(method): continue
            # Get the auto-decorated function and extract click metadata
            decorated = auto_click_decorate_command(method, cls.__all_type_handlers__)

            @click.pass_context
            @functools.wraps(decorated)
            def wrapper(ctx, *args, **kwargs):
                instance = cls()
                # print(f"🧪 DEBUG: calling {method.__name__} with args={args}, kwargs={kwargs}")
                return method(instance, *args, **kwargs)

            # Extract click metadata from the decorated function
            click_params = getattr(decorated, "__click_params__", [])
            click_attrs = getattr(decorated, "__click_attrs__", {})
            cmd = click.Command(name=click_attrs.get("name", method.__name__),
                                callback=wrapper,
                                params=click_params,
                                **click_attrs)
            cls.__group__.add_command(cmd, name=method.__name__)

        cls.__config__ = {}
        if hasattr(cls, "_config") and callable(cls._config):
            cls.__config__ = cls._config()
            cls._log({
                "path": cls.__group__.name,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "message": "Configuration applied",
                "config": cls.__config__
            })

        CliRegistry.register(cls)

        return cls

    def __call__(cls, *args, **kwargs):
        if "_instance" in cls.__dict__:
            return cls.__dict__["_instance"]
        instance = super().__call__(*args, **kwargs)
        cls._instance = instance
        CliLogger.log(instance, "Instance created", event="instance_created")
        return instance

class CLI(metaclass=CliMeta):
    __parent__ = None

    @classmethod
    def get_full_path(cls):
        if parent := cls.__parent__:
            return f"{parent.get_full_path()} {cls.__name__}"
        return cls.__name__

    @classmethod
    def get_command_path(cls):
        path = cls_to_groupname(cls)
        if parent := cls.__parent__:
            path = f"{parent.get_command_path()} {path}"
        return path

    @classmethod
    def _testroot(cls, cmd):
        return click.testing.CliRunner().invoke(cls._root().__group__, cmd)

    @classmethod
    def _test(cls, cmd):
        return click.testing.CliRunner().invoke(cls.__group__, cmd)

    @classmethod
    def _run(cls):
        cls._root.__group__()

    @classmethod
    def _root(cls):
        while cls.__parent__:
            cls = cls.__parent__
        return cls

    @classmethod
    def _walk_click(cls):
        return all_command_names(cls.__group__)

def all_command_names(group: click.Group, prefix=""):
    """
    Recursively prints all command names in a Click group as a comma-separated list.

    Args:
        group (click.Group): The root Click group to inspect.
        prefix (str): Internal use for recursive path tracking.

    Example:
        >>> all_command_names(cli)
        top-level, top-level.subcommand, ...
    """
    commands = []
    print(group.name, group.commands)

    def walk(g: click.Group, path: str):
        # print(g)
        for name, cmd in g.commands.items():
            full_path = f"{path} {name}" if path else name
            commands.append(full_path)
            if isinstance(cmd, click.Group):
                walk(cmd, full_path)

    walk(group, prefix)
    return commands
