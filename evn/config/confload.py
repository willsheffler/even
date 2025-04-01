from pathlib import Path
from collections import ChainMap
import os
import tomllib

XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

CONFIG_PATHS = [
    lambda: load_cli_layer(),
    lambda: load_env_layer("EVN_"),
    lambda: load_toml_layer(XDG_CONFIG_HOME / "dev" / "local" / f"{os.uname().nodename}.toml"),
    lambda: load_toml_layer(Path("local/USER/userconfig.toml")),
    lambda: load_pyproject_toml(Path("pyproject.toml")),
    lambda: load_toml_layer(XDG_CONFIG_HOME / "dev" / "dev_config.toml"),
    lambda: {},  # built-in fallback (can point to static defaults later)
]

def get_config():
    """
    Return merged configuration from all layers using ChainMap.
    """
    layers = [layer() for layer in CONFIG_PATHS]
    return ChainMap(*layers)

def load_toml_layer(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, 'rb') as f:
        return tomllib.load(f)

def load_pyproject_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, 'rb') as f:
        data = tomllib.load(f)
    return data.get("tool", {}).get("evn", {})

def load_env_layer(prefix: str) -> dict:
    result = {}
    for key, val in os.environ.items():
        if key.startswith(prefix):
            parts = key[len(prefix):].lower().split("__")
            ref = result
            for part in parts[:-1]:
                ref = ref.setdefault(part, {})
            ref[parts[-1]] = val
    return result

def load_cli_layer():
    # stub, filled in from evn.cli.config
    return {}
