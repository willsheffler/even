import evn
from evn.testing import TestApp as App

def main():
    # test_set_app_defaults_from_config()
    # return
    evn.maintest(
        namespace=globals(),
        verbose=1,
        check_xfail=False,
        use_test_classes=True,
        # re_only=['test_generic_get_items'],
        re_exclude=[],
    )

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
    config.testapp.version.verbose = True
    evn.cli.set_app_defaults_from_config(App, config)
    config2 = evn.cli.get_config_from_app_defaults(App)
    assert config == config2

def test_set_app_callback_defaults_from_config():
    config = evn.config.get_config(App)
    config.testapp._callback.foo = 'newvall'
    evn.cli.set_app_defaults_from_config(App, config)
    config2 = evn.cli.get_config_from_app_defaults(App)
    if config != config2:
        evn.diff(config, config2, show=True)
        assert config == config2

def test_big_change():
    config = evn.config.get_config(App)
    config.testapp.versionverbose = 1
    config.testapp.doccheckdocsdir = "docsfoo"
    config.testapp._callbackfoo = "barfoo"
    config.testapp.dev.format.streamtab_width = 5
    config.testapp.dev.format.streamlanguage = "pythonfoo"
    config.testapp.dev.format.smartmode = "gitfoo"
    config.testapp.dev.test.filefail_fast = 1
    config.testapp.dev.test.swappath = .
    config.testapp.dev.validate.filestrict = 2
    config.testapp.dev.doc.buildopen_browser = 1
    config.testapp.dev.create.testfilemodule = None
    config.testapp.dev.create.testfiletestfile = .
    config.testapp.dev.create.testfileprompts = 2
    config.testapp.doccheck._callbackdocsdir = "docsfoo"
    config.testapp.doccheck.build.fullforce = 1
    config.testapp.doccheck.open.filebrowser = "firefoxfoo"
    config.testapp.doccheck.doctest.fail-loopverbose = 1
    config.testapp.doccheck.missing.listjson = 1
    config.testapp.qa.matrix.runparallel = 2
    config.testapp.qa.testqa.loopmax_retries = 4
    config.testapp.qa.out.filtermin_lines = 6
    config.testapp.qa.review.coveragemin_coverage = 76
    config.testapp.qa.review.changessummary = 2
    config.testapp.run.dispatch.filepath = None
    config.testapp.run.act.jobname = None
    config.testapp.run.doit.taskname = "foo"
    config.testapp.run.script.shellcmd = None
    config.testapp.buildtools.cpp.compiledebug = 1
    config.testapp.buildtools.cpp.pybindheader_only = 1
    config.testapp.buildtools.clean.allverbose = 1
    config.testapp.proj.rootverbose = 1
    config.testapp.proj.tagsrebuild = 1
    evn.cli.set_app_defaults_from_config(App, config)
    config2 = evn.cli.get_config_from_app_defaults(App)
    if config != config2:
        evn.diff(config, config2, show=True)
        assert config == config2
    assert 0

if __name__ == '__main__':
    main()
