import tempfile
from pathlib import Path
from evn.config import get_config, load_env_layer, load_toml_layer
from evn.cli.cliconf import generate_config_from_cli, DEFAULT_SENTINEL
from evn.tests.cli.evn_test_app import TestCli


def test_env_layer_parsing(monkeypatch):
    monkeypatch.setenv("EVN_FORMAT__TAB_WIDTH", "4")
    monkeypatch.setenv("EVN_DEV__TEST__FAIL_FAST", "true")
    env = load_env_layer("EVN_")
    assert env['format']['tab_width'] == "4"
    assert env['dev']['test']['fail_fast'] == "true"


def test_toml_layer_loading():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".toml", delete=False) as f:
        f.write("""
        [format]
        tab_width = 2

        [dev.test]
        fail_fast = true
        """)
        f.flush()
        fpath = Path(f.name)

    loaded = load_toml_layer(fpath)
    assert loaded['format']['tab_width'] == 2
    assert loaded['dev']['test']['fail_fast'] is True

    fpath.unlink()  # cleanup


def test_generate_config_from_cli():
    config = generate_config_from_cli(TestCli)
    assert isinstance(config, dict)
    assert config['dev']['format']['stream']['tab_width'] == 4
    assert config['dev']['test']['file']['fail_fast'] == False
    assert config['doc']['build']['open_browser'] == False
    assert config['qa']['review']['coverage']['min_coverage'] == 75
    assert config['qa']['review']['changes']['summary'] == True
    assert config['run']['dispatch']['file']['path'] == DEFAULT_SENTINEL


def test_chainmap_includes_all_layers(monkeypatch):
    monkeypatch.setenv("EVN_PROJ__TAGS__REBUILD", "true")
    config = get_config()
    assert config['proj']['tags']['rebuild'] == "true"
