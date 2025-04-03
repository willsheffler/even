import functools

@functools.total_ordering
class Missing:
    __slots__ = ()

    def __repr__(self):
        return 'NA'

    def __eq__(self, other):
        return isinstance(other, Missing)

    def __lt__(self, other):
        return True

NA = Missing()
