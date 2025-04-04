from multipledispatch import dispatch
import rich
import evn

def inspect(obj, **kw):
    return show_impl(obj, **kw)

def show(obj, show=True, flush=True, **kw):
    kw['show'] = show
    with evn.capture_stdio() as printed:
        result = show_impl(obj, **kw)
    printed = printed.read()
    assert not result
    if show and (result or printed):
        with evn.force_stdio():
            # if 'PYTEST_CU66RRENT_TEST' in os.environ:
                # print()
            evn.kwcall(kw, print, printed or result, flush=flush)
    return result

_show = show

def diff(obj1, obj2, show=True, **kw):
    result = diff_impl(obj1, obj2, **kw)
    if show and result: _show(result, **kw)
    return result

@dispatch(object)
def show_impl(obj, **kw):
    """Default show function."""
    rich.inspect(obj, **kw)

@dispatch(object, object)
def diff_impl(obj1, obj2, **kw):
    return set(obj1) ^ set(obj2)
