from pathlib import Path
import enum
import evn
from evn.decon.bunch import Bunch, bunchify

class Action(enum.Enum):
    CONVERT = 443_520
    SET_DEFAULT = 10_200_960
    GET_DEFAULT = 244_823_040

def get_config_from_app_defaults(app):
    """
    Generate a default config structure from a CLI class, including subcommands.
    """
    config = Bunch(_split=' ')

    # return config_app_sync(app, config, Action.GET_DEFAULT)

    def visit(group, path):
        if group.callback:
            config[f'{path} _callback'] = {p.name: p.default for p in group.params}
        for name, method in group.commands.items():
            config[f'{path} {name}'] = {p.name: p.default for p in method.params}

    evn.cli.walk_click_group(app.__group__, visitor=visit)
    return bunchify(config, _like=config)

def config_app_sync(app, config, action: Action):
    # print('config_app_sync', flush=True)
    assert config._conf('split') == ' ', "Config split is not ' '"
    # evn.show(config, name='before', max_width=111)

    def visit(group, path):
        group_items = list(group.commands.items())
        if group.callback:
            group_items.append(('_callback', group))
        for name, method in group_items:
            conf = config._get_split(f'{path} {name}', create=Action.GET_DEFAULT == action)
            for param in method.params:
                assert param.name in conf

                new = param.default
                if isinstance(new,str): new = f'"{new}foo"'
                elif isinstance(new,int): new = new + 1
                elif isinstance(new,float): new = new *2
                elif isinstance(new,bool): new = not new
                elif isinstance(new,Path): new = new.parent
                print(f'config.{'.'.join(path.split())}.{name}{param.name} = {new}')

                if action is Action.CONVERT:
                    conf[param.name] = param.type.convert(conf[param.name], param, None)
                elif action is Action.SET_DEFAULT:
                    if param.default != conf[param.name]:
                        conf[param.name] = param.default
                    param.default = conf[param.name]
                elif action is Action.GET_DEFAULT:
                    conf[param.name] = param.default
                else:
                    raise ValueError(f"Unknown action {action}")

    evn.cli.walk_click_group(app.__group__, visitor=visit)
    return bunchify(config, _like=config)

def convert_config_to_app_types(app, config):
    config_app_sync(app, config, Action.CONVERT)

def set_app_defaults_from_config(app, config):
    config_app_sync(app, config, Action.SET_DEFAULT)

# def get_config_from_app_defaults(app, config):
# config_app_sync(app, config, Action.SET_DEFAULT)
