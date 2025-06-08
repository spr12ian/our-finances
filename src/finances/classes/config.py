import os
from typing import Any


class Config:
    def __init__(self) -> None:
        self._data: dict[str, str] = dict(os.environ)

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def dump(self, prefix: str = "") -> None:
        for k, v in sorted(self._data.items()):
            if k.startswith(prefix):
                print(f"{k}={v}")

    def filter_by_prefix(self, *prefixes: str) -> dict[str, str]:
        return {k: v for k, v in self._data.items() if k.startswith(prefixes)}

    def get(self, name: str, default: Any = None) -> Any:
        if name in self._data:
            return self._data[name]

        if default is not None:
            return default

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )
