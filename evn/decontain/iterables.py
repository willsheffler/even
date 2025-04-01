from typing import Sequence, Any
import numpy as np
import typing
import operator
import evn

T = typing.TypeVar('T')

def nth(thing: evn.Iterable[T], n: int = 0) -> T:
    iterator = iter(thing)
    try:
        for i in range(n):
            next(iterator)
        return next(iterator)
    except StopIteration:
        return None

first = nth

def head(thing: evn.Iterable[T], n=5, *, requireall=False, start=0) -> list[T]:
    iterator, result = iter(thing), []
    try:
        for i in range(start):
            next(iterator)
        for i in range(n):
            result.append(next(iterator))
    except StopIteration:
        if requireall: return None
    return result

def order(seq: Sequence[Any], key=None) -> list[int]:
    return [a[1] for a in sorted(((s, i) for i, s in enumerate(seq)), key=key)]

def reorder(seq: Sequence[T], order: Sequence[int]) -> Sequence[T]:
    return [seq[i] for i in order]

def reorder_inplace(seq: list[Any], order: Sequence[int]) -> None:
    result = reorder(seq, order)
    for i, v in enumerate(result):
        seq[i] = v

def reorderer(order: Sequence[int]) -> evn.Callable[[T], T]:

    def reorder_func(*seqs: list[Any]):
        for seq in seqs:
            reorder_inplace(seq, order)

    return reorder_func

def zipenum(*args):
    for i, z in enumerate(zip(*args)):
        yield i, *z

def subsetenum(n_or_set):
    if isinstance(n_or_set, int): n_or_set = range(n_or_set)
    input_set = set(n_or_set)
    tot = 0
    for size in range(len(input_set), 0, -1):
        for subset in evn.it.combinations(input_set, size):
            yield tot, subset
            tot += 1

def zipmaps(*args: dict[str, T], order='key', intersection=False) -> dict[str, tuple[T, ...]]:
    if not args: raise ValueError('zipmaps requires at lest one argument')
    if intersection: keys = evn.dev.andreduce(set(map(str, a.keys())) for a in args)
    else: keys = evn.decontain.orreduce(set(map(str, a.keys())) for a in args)
    if order == 'key': keys = sorted(keys)
    if order == 'val': keys = sorted(keys, key=lambda k: args[0].get(k, evn.NA))
    result = type(args[0])({k: tuple(a.get(k, evn.NA) for a in args) for k in keys})
    return result

def zipitems(*args, **kw):
    zipped = zipmaps(*args, **kw)
    for k, v in zipped.items():
        yield k, *v

@evn.dc.dataclass
class UniqueIDs:
    alphabet: Sequence = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"
    idmap: dict = evn.dc.field(default_factory=dict)
    offset: int = 0

    def __call__(self, ids: np.ndarray, reset=False):
        if reset:
            self.offset += len(self.idmap)
            self.idmap.clear()
        uniq = set(np.unique(ids))
        for cid in uniq - set(self.idmap):
            self.idmap[str(cid)] = self.alphabet[(len(self.idmap) - self.offset) % len(self.alphabet)]
        newids = evn.copy(ids)
        for u in uniq:
            newids[ids == u] = self.idmap[u]
        # evn.icv(self.idmap)
        return newids


def opreduce(op, iterable):
    """Reduces an iterable using a specified operator or function.

    This function applies a binary operator or callable across the elements of an iterable, reducing it to a single value.
    If `op` is a string, it will look up the corresponding operator in the `operator` module.

    Args:
        op (str | callable): A callable or the name of an operator from the `operator` module (e.g., 'add', 'mul').
        iterable (iterable): The iterable to reduce.

    Returns:
        Any: The reduced value.

    Raises:
        AttributeError: If `op` is a string but not a valid operator in the `operator` module.
        TypeError: If `op` is not a valid callable or operator.

    Example:
        >>> from operator import add, mul
        >>> print(opreduce(add, [1, 2, 3, 4]))  # 10
        10
        >>> print(opreduce('mul', [1, 2, 3, 4]))  # 24
        24
        >>> print(opreduce(lambda x, y: x * y, [1, 2, 3, 4]))  # 24
        24
    """
    if isinstance(op, str):
        op = getattr(operator, op)
    return evn.ft.reduce(op, iterable)

for op in 'add mul matmul or_ and_'.split():
    opname = op.strip('_')
    globals()[f'{opname}reduce'] = evn.ft.partial(opreduce, getattr(operator, op))
