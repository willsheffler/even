import inspect
import evn
import pprint
from evn.decontain.bunch import Bunch

DEFAULT_SENTINEL = None # "__MISSING__"

def generate_config_from_cli(cli_class):
    """
    Generate a default config structure from a CLI class, including subcommands.
    """
    config = Bunch(_split_space=True)

    def visit(group, path):
        for name, method in group.commands.items():
            config[f'{path} {group.name} {name}'] = extract_param_defaults(method)

    evn.cli.walk_click_group(cli_class.__group__, visitor=visit)
    print(config)
    return config

def extract_param_defaults(fn):
    """
    Return dict of parameter defaults for a function, replacing missing values with sentinel.
    """
    sig = inspect.signature(fn)
    result = {}
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if param.default is inspect.Parameter.empty:
            result[name] = DEFAULT_SENTINEL
        else:
            result[name] = param.default
    return result
