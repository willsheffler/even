import click
import datetime
import functools
from evn.cli.auto_click_decorator import auto_click_decorate_command
from evn.cli.cli_registry import CliRegistry
from evn.cli.cli_logger import CliLogger

class CliMeta(type):

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        cls.__group__ = click.Group(name=cls.__name__.removeprefix("CLI").lower())
        CliLogger.log(cls, f"Registered group: {cls.__group__.name}", event="group_registered")
        # print(f"[CliMeta] Registered group for {cls.__name__} -> {cls.__group__.name}")

        cls.__log__ = []

        parent = None
        for base in bases:
            if hasattr(base, "__group__") and base.__name__ != "CliBase":
                parent = base
                base.__group__.add_command(cls.__group__, name=cls.__group__.name)
                break
        cls.__parent__ = parent

        collected = []
        for base in reversed(cls.__mro__):
            if hasattr(base, "click_type_handlers"):
                for h in base.click_type_handlers:
                    if h not in collected:
                        collected.append(h)
        cls.__collected_type_handlers__ = collected

        def log_method(self, message, **kwargs):
            entry = {
                "path": self.get_full_path(),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "message": message,
                **kwargs,
            }
            self.__log__.append(entry)

        cls.log = log_method

        def create_command(method, cls_ref):
            # Get the auto-decorated function and extract click metadata
            decorated = auto_click_decorate_command(method, cls_ref.__collected_type_handlers__)

            @click.pass_context
            @functools.wraps(decorated)
            def wrapper(ctx, *args, **kwargs):
                instance = cls_ref()
                print(f"🧪 DEBUG: calling {method.__name__} with args={args}, kwargs={kwargs}")
                return method(instance, *args, **kwargs)

            # Extract click metadata from the decorated function
            click_params = getattr(decorated, "__click_params__", [])
            click_attrs = getattr(decorated, "__click_attrs__", {})

            return click.Command(name=click_attrs.get("name", method.__name__),
                                 callback=wrapper,
                                 params=click_params,
                                 **click_attrs)

        for attr_name, attr in namespace.items():
            if callable(attr) and not attr_name.startswith("_") and attr.__qualname__.split(".")[0] == name:
                command = create_command(attr, cls)
                cls.__group__.add_command(command, name=attr_name)
            # Register nested CliBase subclasses as subcommands
            elif hasattr(attr, "__group__") and isinstance(attr.__group__, click.Group):
                cls.__group__.add_command(attr.__group__, name)
                setattr(attr.__class__, "__parent__", cls)


        cls.__config__ = {}
        if hasattr(cls, "_config") and callable(cls._config):
            cls.__config__ = cls._config()
            cls.__log__.append({
                "path": cls.__group__.name,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "message": "Configuration applied",
                "config": cls.__config__
            })
        CliLogger.log(cls, "Configuration applied", event="config", data=cls.__config__)

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
    click_type_handlers = []

    def get_full_path(self):
        parent = self.__class__.__parent__
        if parent and parent.__name__ != "CliBase":
            return parent.__name__ + "." + self.__class__.__name__
        return self.__class__.__name__

    def run(self):
        root = self.__class__
        while root.__parent__:
            root = root.__parent__
        root().__group__()
