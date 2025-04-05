import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    cast as cast,
    IO,
    Iterator,
    TypeVar,
    Union,
    Iterable,
    Mapping,
    MutableMapping,
    Sequence,
    MutableSequence,
)
if sys.version_info.minor >= 10:
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

KW = dict[str, Any]
IOBytes = IO[bytes]
IO = IO[str]
"""Type alias for keyword arguments represented as a dictionary with string keys and any type of value."""

FieldSpec = Union[str, list[str], tuple[str], Callable[..., str], tuple]
EnumerIter = Iterator[int]
EnumerListIter = Iterator[list[Any]]

T = TypeVar('T')
R = TypeVar('R')
C = TypeVar('C')
if sys.version_info.minor >= 10 or TYPE_CHECKING:
    P = ParamSpec('P')
    F = Callable[P, R]
else:
    P = TypeVar('P')
    P.args = list[Any]
    P.kwargs = KW
    F = Callable[[Any, ...], R]

def basic_typevars(which) -> list[Union[TypeVar, ParamSpec]]:
    result = [globals()[k] for k in which]
    return result

def isstr(s: Any) -> bool:
    return isinstance(s, str)

def isint(s: Any) -> bool:
    return isinstance(s, int)

def islist(s: Any) -> bool:
    return isinstance(s, list)

def isdict(s: Any) -> bool:
    return isinstance(s, dict)

def isseq(s: Any) -> bool:
    return isinstance(s, Sequence)

def ismap(s: Any) -> bool:
    return isinstance(s, Mapping)

def isseqmut(s: Any) -> bool:
    return isinstance(s, MutableSequence)

def ismapmut(s: Any) -> bool:
    return isinstance(s, MutableMapping)

def isiter(s: Any) -> bool:
    return isinstance(s, Iterable)

