# evn/cli/cli_registry.py
from typing import Type, List, Dict
import click

class CliRegistry:
    """
    Global registry to track all CLI classes that use CliMeta.
    Used for diagnostics, testing, and reset functionality.
    """
    _cli_classes: List[Type] = []

    @classmethod
    def register(cls, cli_class: Type) -> None:
        if cli_class not in cls._cli_classes:
            cls._cli_classes.append(cli_class)
        else:
            raise ValueError(f"CLI class {cli_class.__name__} is already registered.")

    @classmethod
    def all_cli_classes(cls) -> List[Type]:
        return list(cls._cli_classes)

    @classmethod
    def get_root_commands(cls) -> Dict[str, click.Group]:
        roots = {}
        for c in cls._cli_classes:
            if getattr(c, "__parent__", None) is None:
                roots[c.__group__.name] = c.__group__
        return roots

    @classmethod
    def reset(cls) -> None:
        for c in cls._cli_classes:
            if hasattr(c, "_instance"):
                del c._instance
            if hasattr(c, "__log__"):
                c.__log__.clear()
            if hasattr(c, "__config__"):
                del c.__config__

    @classmethod
    def print_summary(cls) -> None:
        print("\n📦 CLI Registry Summary:")
        for c in cls._cli_classes:
            print(f"- {c.__name__}")
            if hasattr(c, "__group__"):
                print(f"  └── group: {c.__group__.name}")
            if hasattr(c, "__parent__") and c.__parent__:
                print(f"  └── parent: {c.__parent__.__name__}")
            if hasattr(c, "click_type_handlers"):
                print(f"  └── handlers: {[h.__class__.__name__ for h in c.click_type_handlers]}")
            print()
