import evn
from evn.testing import TestApp as App

def test_convert_config_to_app_types():
    config = evn.config.get_config(App)
    assert config._conf('split') == ' '
    assert config.testapp._conf('split') == ' '
    assert config.testapp._conf('split') == ' '
    assert config.testapp.doccheck._conf('split') == ' '
    # evn.config.print_config(config)
    config = evn.cli.convert_config_to_app_types(App, config)

def test_set_app_defaults_from_config():
    config = evn.config.get_config(App)
    # evn.config.print_config(config)
    # evn.show(config, method='yaml')
    # evn.show(config, method='tree', max_width=100e)
    # evn.show(config, method='rich')
    config.testapp._callback.foo = 'TESTFOO'
    evn.cli.set_app_defaults_from_config(App, config)
    config2 = evn.cli.get_config_from_app_defaults(App)
    print(flush=True)
    diff = evn.diff(config, config2, method='fancy', flatpaths=True)
    print(flush=True)
    assert config == config2
