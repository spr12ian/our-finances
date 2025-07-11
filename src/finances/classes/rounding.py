import decimal
from functools import cache
from typing import ClassVar


class RoundingError(Exception):
    pass


class Rounding:
    """Central definition of rounding modes from Decimal."""

    CEILING: ClassVar[str] = "ROUND_CEILING"
    DOWN: ClassVar[str] = "ROUND_DOWN"
    FLOOR: ClassVar[str] = "ROUND_FLOOR"
    HALF_DOWN: ClassVar[str] = "ROUND_HALF_DOWN"
    HALF_EVEN: ClassVar[str] = "ROUND_HALF_EVEN"
    HALF_UP: ClassVar[str] = "ROUND_HALF_UP"
    UP: ClassVar[str] = "ROUND_UP"
    ROUND_05UP: ClassVar[str] = "ROUND_05UP"

    @classmethod
    def from_constant(cls, const: str) -> str:
        for name in cls.__annotations__:
            if getattr(decimal, getattr(cls, name)) == const:
                return getattr(cls, name)
        raise RoundingError(f"Unknown constant: {const}")

    @classmethod
    def is_valid(cls, rounding: str) -> bool:
        return rounding in cls.values()

    @classmethod
    def to_constant(cls, rounding: str) -> str:
        try:
            return getattr(decimal, rounding)
        except AttributeError as e:
            raise RoundingError(f"Invalid rounding mode: {rounding}") from e

    @classmethod
    @cache
    def values(cls) -> set[str]:
        return {getattr(cls, name) for name in cls.__annotations__}
