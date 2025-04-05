import os
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
            if 'PYTEST_CURRENT_TEST' in os.environ: print()
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

@evn.lazydispatch
def summary(obj, **kw) -> str:
    if hasattr(obj, 'summary'): return obj.summary()
    if isinstance(obj, (list, tuple)): return str([summary(o, **kw) for o in obj])
    return obj

@summary.register('numpy.ndarray')
def summary(array, maxnumel):
    if array.size <= maxnumel:
        return str(array)
    return f'{array.__class__.__name__}{list(array.shape)}'

@summary.register('torch.Tensor')
def summary(tensor, maxnumel):
    if tensor.numel <= maxnumel:
        return str(tensor)
    return f'{tensor.__class__.__name__}{list(tensor.shape)}'
