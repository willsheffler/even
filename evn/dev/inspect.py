import os
from multipledispatch import dispatch
import rich
import evn

def inspect(obj, **kw):
    return show_impl(obj, **kw)

def show(obj, show=True, **kw):
    kw['show'] = show
    result = show_impl(obj, **kw)
    assert not result
    if show and result:
        with evn.force_stdio():
            if 'PYTEST_CURRENT_TEST' in os.environ:
                print()
            evn.kwcall(kw, print, result, flush=True)
            assert 0
    return result

def diff(obj1, obj2, show=True, **kw):
    kw['show'] = show
    result = diff_impl(obj1, obj2, **kw)
    if show and result:
        with evn.force_stdio():
            evn.kwcall(kw, print, result, flush=True)
    return diff_impl(obj1, obj2, **kw)

@dispatch(object)
def show_impl(obj, **kw):
    """Default show function."""
    rich.inspect(obj, **kw)

@dispatch(object, object)
def diff_impl(obj1, obj2, **kw):
    return set(obj1) ^ set(obj2)
