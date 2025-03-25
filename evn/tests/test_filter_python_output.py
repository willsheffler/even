import difflib
import pytest
import evn

def main():
    pass

def helper_test_filter_python_output(text, ref, preset):
    result = evn.filter_python_output(text, preset=preset, minlines=0)
    if result != ref:
        diff = difflib.ndiff(result.splitlines(), ref.splitlines())
        print('\nDIFF:', flush=True)
        print('\n'.join(f'NDIFF {d}' for d in diff), flush=True)
        assert len(result.splitlines()) == len(result.splitlines())
        # assert 0, 'filter mismatch'

@pytest.mark.xfail
def test_filter_python_output_whitespace():
    result = evn.filter_python_output("    \n" * 7, preset='boilerplate')
    assert result.count('\n') == 1

def test_filter_python_output_mid():
    helper_test_filter_python_output(midtext, midfiltered, preset='boilerplate')

def test_filter_python_output_small():
    helper_test_filter_python_output(smalltext, smallfiltered, preset='boilerplate')

def test_filter_python_output_error():
    helper_test_filter_python_output(errortext, errorfiltered, preset='boilerplate')

def test_analyze_python_errors_log():
    log = '''Traceback (most recent call last):
  File "example.py", line 10, in <module>
    1/0
ZeroDivisionError: division by zero'''
    result = evn.analyze_python_errors_log(log)
    # print(result)
    assert 'Unique Stack Traces Report (1 unique traces):' in result
    assert 'ZeroDivisionError: division by zero' in result

def test_create_errors_log_report():
    trace_map = {
        ('1/0', 'division by zero'):
        '''Traceback (most recent call last):
  File "example.py", line 10, in <module>
    1/0
ZeroDivisionError: division by zero'''
    }

    report = evn.create_errors_log_report(trace_map)
    assert 'Unique Stack Traces Report (1 unique traces):' in report
    assert 'ZeroDivisionError: division by zero' in report

def test_multiple_unique_traces():
    log = '''Traceback (most recent call last):
  File "example.py", line 10, in <module>
    1/0
ZeroDivisionError: division by zero

Traceback (most recent call last):
  File "example.py", line 20, in <module>
    x = int("abc")
ValueError: invalid literal for int()'''

    result = evn.analyze_python_errors_log(log)
    assert 'Unique Stack Traces Report (2 unique traces):' in result
    assert 'ZeroDivisionError: division by zero' in result
    assert 'ValueError: invalid literal for int()' in result

def test_similar_traces_are_grouped():
    log = '''Traceback (most recent call last):
  File "example.py", line 13, in <module>
    1/0
ZeroDivisionError: division by zero

Traceback (most recent call last):
  File "example.py", line 13, in <module>
    1/0
ZeroDivisionError: division by zero'''

    result = evn.analyze_python_errors_log(log)
    assert 'Unique Stack Traces Report (1 unique traces):' in result
    assert 'ZeroDivisionError: division by zero' in result
    assert result.count('ZeroDivisionError') == 1

def test_different_lines_are_not_grouped():
    log = '''Traceback (most recent call last):
  File "example.py", line 10, in <module>
    1/0
ZeroDivisionError: division by zero

Traceback (most recent call last):
  File "example.py", line 15, in <module>
    1/0
ZeroDivisionError: division by zero'''

    result = evn.analyze_python_errors_log(log)
    assert 'Unique Stack Traces Report (2 unique traces):' in result
    assert 'ZeroDivisionError: division by zero' in result
    assert result.count('ZeroDivisionError') == 2

# ######################### test data #######################
errortext = """maintest /home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py:
Traceback (most recent call last):
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 151, in <module>
    main()
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 6, in main
    TEST.tests.maintest(namespace=globals())
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 40, in maintest
    _maintest_run_test_function(name, func, result, nofail, fixtures, funcsetup, kw)
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 80, in _maintest_run_test_function
    TEST.dev.call_with_args_from(fixtures, func, **kw)
  File "/home/sheffler/rfd/TEST.dev.decorators.py", line 33, in call_with_args_from
    return func(**args)
           ^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 19, in test_filter_python_output_small
    helper_test_filter_python_output(smalltext, smallfiltered, preset='boilerplate')
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
NameError: name 'helper_test_filter_python_output' is not defined
Times(name=Timer, order=longest, summary=sum):
    maintest *    0.39438
============== run_tests_on_file.py done, time   0.611 ==============
"""
errorfiltered = """maintest /home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py:
Traceback (most recent call last):
  test_filter_python_output.py -> main -> maintest -> _maintest_run_test_function -> call_with_args_from ->
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 19, in test_filter_python_output_small
    helper_test_filter_python_output(smalltext, smallfiltered, preset='boilerplate')
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
NameError: name 'helper_test_filter_python_output' is not defined
Times(name=Timer, order=longest, summary=sum):
    maintest *    0.39438
============== run_tests_on_file.py done, time   0.611 ==============
"""

midtext = """maintest /home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py:
==============test_sym_detect_frames_noised_T===============
Traceback (most recent call last):
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py", line 185, in <module>
    main()
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py", line 25, in main
    TEST.tests.maintest(namespace=globals(), config=config_test, verbose=1)
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/maintest.py", line 40, in maintest
    _maintest_run_test_function(name, func, result, nofail, fixtures, funcsetup, kw)
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/maintest.py", line 93, in _maintest_run_test_function
    elif error: raise error
                ^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/maintest.py", line 80, in _maintest_run_test_function
    TEST.dev.call_with_args_from(fixtures, func, **kw)
  File "/home/sheffler/rfd/lib/TEST/TEST.dev.decorators.py", line 33, in call_with_args_from
    return func(**args)
           ^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py", line 76, in func_noised
    sinfo = helper_test_frames(nframes, symid, ideal=False)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py", line 30, in helper_test_frames
    TEST.icv(tol)
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/site-packages/icecream/icecream.py", line 208, in __call__
    out = self._format(callFrame, *args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/site-packages/icecream/icecream.py", line 242, in _format
    out = self._formatArgs(
          ^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/site-packages/icecream/icecream.py", line 255, in _formatArgs
    out = self._constructArgumentOutput(prefix, context, pairs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/site-packages/icecream/icecream.py", line 262, in _constructArgumentOutput
    pairs = [(arg, self.argToStringFunction(val)) for arg, val in pairs]
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/functools.py", line 909, in wrapper
    return dispatch(args[0].__class__)(*args, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/site-packages/icecream/icecream.py", line 183, in argumentToString
    s = DEFAULT_ARG_TO_STRING_FUNCTION(obj)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/pprint.py", line 62, in pformat
    underscore_numbers=underscore_numbers).pformat(object)
                                           ^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/pprint.py", line 161, in pformat
    self._format(object, sio, 0, 0, {}, 0)
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/pprint.py", line 178, in _format
    rep = self._repr(object, context, level)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/pprint.py", line 458, in _repr
    repr, readable, recursive = self.format(object, context.copy(),
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/pprint.py", line 471, in format
    return self._safe_repr(object, context, maxlevels, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/sw/MambaForge/envs/rfdsym312/lib/python3.12/pprint.py", line 632, in _safe_repr
    rep = repr(object)
          ^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/dev/tolerances.py", line 52, in __repr__
    TEST.dev.print_table(self.kw)
  File "/home/sheffler/rfd/lib/TEST/TEST/dev/format.py", line 21, in print_table
    table = make_table(thing, **kw)
            ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/dev/format.py", line 14, in make_table
    if isinstance(thing, dict): return make_table_dict(thing, **kw)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/dev/format.py", line 37, in make_table_dict
    assert isinstance(mapping, Mapping) and mapping
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
Times(name=Timer, order=longest, summary=sum):
    test_sym_detect.py:func_noised      0.43416
                          maintest *    0.39847
                     sym.py:frames      0.03893
Traceback (most recent call last):
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 92, in <module>
    main()
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 6, in main
    TEST.tests.maintest(namespace=globals())
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 40, in maintest
    _maintest_run_test_function(name, func, result, nofail, fixtures, funcsetup, kw)
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 93, in _maintest_run_test_function
    elif error: raise error
                ^^^^^^^^^^^
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 80, in _maintest_run_test_function
    TEST.dev.call_with_args_from(fixtures, func, **kw)
  File "/home/sheffler/rfd/TEST.dev.decorators.py", line 33, in call_with_args_from
    return func(**args)
           ^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 13, in test_filter_python_output
    assert 0
           ^
AssertionError

"""

midfiltered = """maintest /home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py:
==============test_sym_detect_frames_noised_T===============
Traceback (most recent call last):
  test_sym_detect.py -> main -> maintest -> _maintest_run_test_function -> _maintest_run_test_function -> call_with_args_from ->
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py", line 76, in func_noised
    sinfo = helper_test_frames(nframes, symid, ideal=False)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/sym/test_sym_detect.py", line 30, in helper_test_frames
    TEST.icv(tol)
  __call__ -> _format -> _formatArgs -> _constructArgumentOutput -> wrapper -> argumentToString -> pformat -> pformat -> _format -> _repr -> format -> _safe_repr ->
  File "/home/sheffler/rfd/lib/TEST/TEST/dev/tolerances.py", line 52, in __repr__
    TEST.dev.print_table(self.kw)
  print_table -> make_table ->
  File "/home/sheffler/rfd/lib/TEST/TEST/dev/format.py", line 37, in make_table_dict
    assert isinstance(mapping, Mapping) and mapping
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
Times(name=Timer, order=longest, summary=sum):
    test_sym_detect.py:func_noised      0.43416
                          maintest *    0.39847
                     sym.py:frames      0.03893
Traceback (most recent call last):
  test_filter_python_output.py -> main -> maintest -> _maintest_run_test_function -> _maintest_run_test_function -> call_with_args_from ->
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 13, in test_filter_python_output
    assert 0
           ^
AssertionError
"""

smalltext = """extra text at the start
Traceback (most recent call last):
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 92, in <module>
    main()
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 6, in main
    TEST.tests.maintest(namespace=globals())
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 40, in maintest
    _maintest_run_test_function(name, func, result, nofail, fixtures, funcsetup, kw)
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 93, in _maintest_run_test_function
    elif error: raise error
                ^^^^^^^^^^^
  File "/home/sheffler/rfd/TEST/tests/maintest.py", line 80, in _maintest_run_test_function
    TEST.dev.call_with_args_from(fixtures, func, **kw)
  File "/home/sheffler/rfd/TEST.dev.decorators.py", line 33, in call_with_args_from
    return func(**args)
           ^^^^^^^^^^^^
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 13, in test_filter_python_output
    assert 0
           ^
AssertionError
extra text at the end
"""

smallfiltered = """extra text at the start
Traceback (most recent call last):
  test_filter_python_output.py -> main -> maintest -> _maintest_run_test_function -> _maintest_run_test_function -> call_with_args_from ->
  File "/home/sheffler/rfd/lib/TEST/TEST/tests/dev/code/test_filter_python_output.py", line 13, in test_filter_python_output
    assert 0
           ^
AssertionError
extra text at the end
"""

if __name__ == '__main__':
    main()
