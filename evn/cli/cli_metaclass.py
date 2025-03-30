import click
import datetime
import functools
import typing
from evn.cli.auto_click_decorator import auto_click_decorate_command
from evn.cli.cli_registry import CliRegistry
from evn.cli.cli_logger import CliLogger
from evn.cli.click_type_handler import ClickTypeHandlers

class CliMeta(type):
    # there are NOT ACTUALLY USED just to make the type checker happy
    __group__: click.Group
    __parent__: 'CliBase | None'
    __type_handlers__: ClickTypeHandlers
    __config__: dict
    _config: classmethod
    _log: typing.Callable[['dict|str'], None]

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        @classmethod
        def log(cls, *a, **kw):
            CliLogger.log(cls, *a, **kw)

        cls._log, cls.__log__ = log, []

        cls.__group__ = click.Group(name=cls.__name__.removeprefix("CLI").lower())
        CliLogger.log(cls, f"Registered group: {cls.__group__.name}", event="group_registered")
        # print(f"[CliMeta] Registered group for {cls.__name__} -> {cls.__group__.name}")

        parent = None
        for base in bases:
            if hasattr(base, "__group__") and base.__name__ != "CliBase":
                parent = base
                base.__group__.add_command(cls.__group__, name=cls.__group__.name)
                break
        cls.__parent__ = parent

        cls.__type_handlers__ = ClickTypeHandlers()
        for base in reversed(cls.__mro__):
            cls.__type_handlers__ |= set(getattr(base, 'click_type_handlers', set()))

        def create_command(method, cls_ref):
            # Get the auto-decorated function and extract click metadata
            decorated = auto_click_decorate_command(method, cls_ref.__type_handlers__)

            @click.pass_context
            @functools.wraps(decorated)
            def wrapper(ctx, *args, **kwargs):
                instance = cls_ref()
                # print(f"🧪 DEBUG: calling {method.__name__} with args={args}, kwargs={kwargs}")
                return method(instance, *args, **kwargs)

            # Extract click metadata from the decorated function
            click_params = getattr(decorated, "__click_params__", [])
            click_attrs = getattr(decorated, "__click_attrs__", {})

            return click.Command(name=click_attrs.get("name", method.__name__),
                                 callback=wrapper,
                                 params=click_params,
                                 **click_attrs)

        # add click decorategd member functions
        for attr_name, attr in namespace.items():
            if callable(attr) and not attr_name.startswith("_") and attr.__qualname__.split(".")[0] == name:
                command = create_command(attr, cls)
                cls.__group__.add_command(command, name=attr_name)

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

class CliBase(metaclass=CliMeta):
    __group__: click.Group
    __parent__: 'CliBase | None'
    __type_handlers__ = ClickTypeHandlers
    __config__: dict
    _config: classmethod
    _clslog: classmethod
    _log: typing.Callable[['CliBase', 'dict|str'], None]
    __log__: list[str]
    click_type_handlers = []

    @classmethod
    def get_full_path(cls):
        parent = cls.__parent__
        if parent and parent.__name__ != "CliBase":
            return f"{parent.get_full_path()}.{cls.__name__}"
        return cls.__name__

    @classmethod
    def get_command_path(cls):
        path = cls.__name__.removeprefix("CLI").lower()
        parent = cls.__parent__
        if parent and parent.__name__ != "CliBase":
            path = f"{parent.get_command_path()}.{path}"
        return path

    def _run(self):
        root: type = self.__class__
        while root.__parent__:
            root = root.__parent__
        root().__group__()
