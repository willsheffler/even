from time import perf_counter

_start, _timings = perf_counter(), dict()

def evn_init_checkpoint(name):
    global _start, _timings
    _timings[name] = [perf_counter() - _start]
    _start = perf_counter()

import contextlib
import os
import typing
import dataclasses as dc  # noqa
import functools as ft  # noqa
import itertools as it  # noqa
import contextlib as cl  # noqa
from pathlib import Path as Path
from copy import copy as copy, deepcopy as deepcopy
from typing import (
    TYPE_CHECKING as TYPE_CHECKING,
    Any as Any,
    Callable as Callable,
    cast as cast,
    Iterator as Iterator,
    TypeVar as TypeVar,
    Union as Union,
    Iterable as Iterable,
    Mapping as Mapping,
    MutableMapping as MutableMapping,
    Sequence as Sequence,
    MutableSequence as MutableSequence,
    Optional as Optional,
)

pkgroot = Path(__file__).parent.absolute()
projroot = pkgroot.parent

evn_init_checkpoint('INIT evn basic imports')
from evn._prelude.version import __version__ as __version__
from evn._prelude.wraps import wraps as wraps
from evn._prelude.import_util import (
    is_installed as is_installed,
    not_installed as not_installed,
    cherry_pick_import as cherry_pick_import,
    cherry_pick_imports as cherry_pick_imports,
)
from evn._prelude.lazy_import import (
    lazyimport as lazyimport,
    lazyimports as lazyimports,
    maybeimport as maybeimport,
    maybeimports as maybeimports,
    LazyImportError as LazyImportError,
)
from evn._prelude.structs import (
    struct as struct,
    mutablestruct as mutablestruct,
    basestruct as basestruct,
    field as field,
)
from evn._prelude.typehints import (
    KW as KW,
    T as T,
    R as R,
    C as C,
    P as P,
    F as F,
    isstr as isstr,
    isint as isint,
    islist as islist,
    isdict as isdict,
    isseq as isseq,
    ismap as ismap,
    isseqmut as isseqmut,
    ismapmut as ismapmut,
    isiter as isiter,
    Vec as Vec,
    Point as Point,
    FieldSpec as FieldSpec,
    EnumerIter as EnumerIter,
    EnumerListIter as EnumerListIter,
    basic_typevars as basic_typevars,
)
# from evn._prelude.chrono import Chrono as Chrono, chrono as chrono, checkpoint as checkpoint
from evn.decontain import iterize_on_first_param, item_wise_operations, subscriptable_for_attributes

from evn.decontain.iterables import zipmaps, zipitems
from evn.meta import NA as NA, kwcall as kwcall
from evn import dev, doc, format, meta
from evn.print import make_table
from evn.cli import CLI

from icecream import ic as ic
ic.configureOutput(includeContext=True)
import builtins
builtins.ic = ic  # make ic available globally

# optional_imports = cherry_pick_import('evn.dev.contexts.optional_imports')
# capture_stdio = cherry_pick_import('evn.dev.contexts.capture_stdio')
# ic, icm, icv = cherry_pick_imports('evn.dev.debug', 'ic icm icv')
# timed = cherry_pick_import('evn.dev.instrumentation.timer.timed')
# item_wise_operations = cherry_pick_import('evn.dev.item_wise.item_wise_operations')
# subscriptable_for_attributes = cherry_pick_import('evn.dev.decorators.subscriptable_for_attributes')
# iterize_on_first_param = cherry_pick_import('evn.dev.decorators.iterize_on_first_param')

# _global_chrono = None

# evn_init_checkpoint('INIT evn prelude imports')

# from evn.dev.error import panic as panic
# from evn.dev.meta import kwcheck as kwcheck, kwcall as kwcall, kwcurry as kwcurry
# from evn.dev.metadata import get_metadata as get_metadata, set_metadata as set_metadata
# from evn.dev.functional import map as map, visit as visit
# from evn.dev.format import print_table as print_table, print as print
# from evn.bunch import Bunch as Bunch, bunchify as bunchify, unbunchify as unbunchify
# from evn.observer import hub as hub
# from evn.dev.tolerances import Tolerances as Tolerances
# from evn.dev.iterables import first as first
# from evn.dev.contexts import stdio as stdio, catch_em_all as catch_em_all

# evn_init_checkpoint('INIT evn from subpackage imports')
# from evn import dev as dev, homog as homog

# if typing.TYPE_CHECKING:
#     from evn import crud

#     import evn.homog.thgeom as htorch
#     import evn.homog.hgeom as hnumpy
#     from evn import pdb
#     from evn import protocol
#     from evn import sel
#     from evn import sym
#     from evn import ml
#     from evn import motif
#     from evn import atom
#     from evn import tools
#     from evn import tests
#     # from evn import fit
#     # from evn import samp
#     # from evn import voxel
# else:
#     atom = lazyimport('evn.atom')
#     crud = lazyimport('evn.crud')
#     cuda = lazyimport('evn.dev.cuda')
#     h = lazyimport('evn.homog.thgeom')
#     hnumpy = lazyimport('evn.homog.hgeom')
#     htorch = lazyimport('evn.homog.thgeom')
#     ml = lazyimport('evn.ml')
#     motif = lazyimport('evn.motif')
#     pdb = lazyimport('evn.pdb')
#     protocol = lazyimport('evn.protocol')
#     qt = lazyimport('evn.dev.qt')
#     sel = lazyimport('evn.sel')
#     sym = lazyimport('evn.sym')
#     tests = lazyimport('evn.tests')
#     tools = lazyimport('evn.tools')
#     # fit = lazyimport('evn.fit')
#     # samp = lazyimport('>evn.samp')
#     # voxel = lazyimport('evn.voxel')
# viz = lazyimport('evn.viz')
# evn_init_checkpoint('INIT evn subpackage imports')

# with contextlib.suppress(ImportError):
#     import builtins

#     setattr(builtins, 'ic', ic)

# def showme(*a, **kw):
#     if all(homog.viz.can_showme(a, **kw)):
#         return homog.viz.showme(a, **kw)
#     from evn.viz import showme as viz_showme

#     viz_showme(*a, **kw)

# # from evn.project_config import install_evn_pre_commit_hook
# # install_evn_pre_commit_hook(projdir, '..')
# # evn_init_checkpoint('INIT evn pre commit hook')

# if _global_chrono: _global_chrono.checkpoints.update(_timings)
# else: _global_chrono = Chrono(checkpoints=_timings)
# dev.global_timer.checkpoints.update(_timings)

# caching_enabled = True
