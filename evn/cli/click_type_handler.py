# click_type_handler.py
import contextlib
import typing
import enum
from functools import lru_cache
import click

class MetadataPolicy(str, enum.Enum):
    FORBID = "no_metadata"
    OPTIONAL = "optional_metadata"
    REQUIRED = "require_metadata"

class DummyParamType(click.ParamType):

    def __bool__(self):
        return False

    def convert(self, value, param, ctx):
        """Dummy conversion that always fails."""
        raise ValueError("DummyParamType should not be used for conversion.")

class ClickTypeHandlers(set):
    """
    A container for Click type handlers.

    This class is used to manage a list of type handlers.
    It can be used to retrieve the appropriate handler for a given type.
    """

    def ordered_handlers(self, basetype, metadata):
        return list(reversed(sorted(self)))

    def typehint_to_click_paramtype(self, basetype, metadata) -> click.ParamType:
        """Given a basetype and optional metadata, return the Click ParamType to use."""
        handlers = [h for h in self if h.metadata_policy(basetype)]
        if metadata:
            for handler_class in handlers:
                if handler_class.metadata_policy(basetype) == MetadataPolicy.REQUIRED:
                    with contextlib.suppress(ValueError):
                        return get_cached_paramtype(handler_class, basetype, metadata)
            for handler_class in handlers:
                if handler_class.metadata_policy(basetype) == MetadataPolicy.OPTIONAL:
                    with contextlib.suppress(ValueError):
                        return get_cached_paramtype(handler_class, basetype)
        for handler_class in handlers:
            with contextlib.suppress(ValueError):
                return get_cached_paramtype(handler_class, basetype)
        return DummyParamType()

class ClickTypeHandler(click.ParamType):
    """
    Base class for handling conversion of type hints to Click ParamTypes.

    Subclasses should define:
      - supported_types: a dict mapping types (e.g., int, list[int]) to booleans.
        The boolean is True if the handler requires metadata for that type.
      - _priority_bonus: an integer bonus (default 0) that subclasses can override.
      - METADATA_BONUS: a fixed bonus (default 10) applied if metadata is used.

    This class provides default no-op implementations for preprocess_value and postprocess_value.
    It also defines a method 'typehint_to_click_paramtype' (the conversion function)
    and a priority computation function.
    """
    # Dictionary of types this handler applies to.
    # Example: {int: False, float: False, list: True}
    supported_types: dict[type, MetadataPolicy] = {}
    _priority_bonus = 0
    METADATA_BONUS = 10

    def __init__(self):
        super().__init__()

    @classmethod
    def metadata_policy(cls, basetype):
        return cls.supported_types.get(basetype)

    def typehint_to_click_paramtype(self, basetype, metadata):
        """
        Given a type hint (basetype) and optional metadata, return the Click ParamType to use.
        Default behavior is to return self if this handler handles the type; otherwise, raises ValueError.
        """
        if not self.handles_type(basetype, metadata):
            raise ValueError(
                f"{self.__class__.__name__} does not handle type {basetype} with metadata {metadata}")
        return self

    def handles_type(self, basetype, metadata=None):
        """
        Check whether this handler applies to the given basetype.
        Iterates over supported_types; if a key matches basetype, then if the boolean flag is True,
        metadata must be provided (and non-empty) for a positive result.
        """
        for typ, metapol in self.supported_types.items():
            # print(typ, basetype, metadata, metapol)
            if issubclass(basetype, typ):
                if metapol == MetadataPolicy.REQUIRED: return bool(metadata)
                if metapol == MetadataPolicy.FORBID: return not metadata
                return True
        return False

    def preprocess_value(self, raw: str):
        """
        Preprocess the raw input value before Click's conversion.
        Default implementation is a aano-op.
        """
        return raw

    def postprocess_value(self, value):
        """
        Postprocess the value after Click's conversion.
        Default implementation is a no-op.
        """
        return value

    def convert(self, value, param, ctx):
        """
        Override click.ParamType.convert to incorporate pre- and post-processing.
        By default, this implementation simply returns the preprocessed value.
        Subclasses should override this method if further conversion is needed.
        """
        try:
            preprocessed = self.preprocess_value(value)
            # Default conversion: return the preprocessed value unchanged.
            converted = preprocessed
            postprocessed = self.postprocess_value(converted)
            return postprocessed
        except Exception as e:
            self.fail(f"Conversion failed for value {value}: {e}", param, ctx)

    def type_specificity(self, basetype):
        """
        Compute a basic measure of specificity for the basetype.
        For generic types (with __args__), count the number of arguments that are not typing.Any.
        """
        if hasattr(basetype, '__args__') and basetype.__args__:
            specificity = sum(1 for arg in basetype.__args__ if arg is not typing.Any)
            return specificity
        return 0

    # def compute_priority(self, basetype, metadata, mro_rank: int):
    #     """
    #    Compute the overall priority for this handler.
    #    Lower numeric values are better.
    #    Priority is computed as:
    #        mro_rank + _priority_bonus + (METADATA_BONUS if metadata is required and provided#) + type_specificity
    #    """
    #     specificity = self.type_specificity(basetype)
    #     bonus = self._priority_bonus
    #     if self.handles_type(basetype, metadata):
    #         for typ, metadata_policy in self.supported_types.items():
    #             if basetype == typ and metadata_policy:
    #                 bonus += self.METADATA_BONUS
    #                 break
    #     return mro_rank + bonus + specificity

# Caching function: cache the computed Click ParamType based on handler class, basetype, and metadata.
@lru_cache(maxsize=None)
def get_cached_paramtype(handler_class, basetype, metadata=None):
    """
    Retrieve (or compute and cache) the Click ParamType for the given handler class, basetype, and metadata.
    """
    handler = handler_class()
    return handler.typehint_to_click_paramtype(basetype, metadata)
