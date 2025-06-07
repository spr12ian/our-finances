import os
from pathlib import Path
from typing import Any

import yaml


class ConfigNode:
    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __init__(self, data: dict[str, Any], path: list[str] | None = None):
        self._data = data or {}
        self._path = path or []

        for key, value in self._data.items():
            if isinstance(value, dict):
                # Recursively nest sub-configs
                setattr(self, key, ConfigNode(value, self._path + [key]))  # type: ignore
            else:
                # Set terminal values with environment override
                setattr(self, key, self._get_value_with_override(key, value))

    def _get_value_with_override(self, key: str, original_value: Any) -> Any:
        env_key = "_".join(self._path + [key]).upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._cast_type(env_value, original_value)
        return original_value

    def _cast_type(self, env_value: str, original_value: Any) -> Any:
        if original_value is None:
            return env_value
        if isinstance(original_value, bool):
            return env_value.lower() in ("1", "true", "yes", "on")
        if isinstance(original_value, int):
            return int(env_value)
        if isinstance(original_value, float):
            return float(env_value)
        return env_value

    def get(self, dotted_key: str, default: Any = None) -> Any:
        keys = dotted_key.split(".")
        node = self
        path: list[str] = []
        for key in keys:
            path.append(key)
            if hasattr(node, key):
                node = getattr(node, key)
            else:
                # Attempt environment fallback
                env_key = "_".join(path).upper()
                env_value = os.getenv(env_key)
                if env_value is not None:
                    return env_value
                return default
        return node


class Config(ConfigNode):
    def __init__(self, yaml_path: Path = Path("config.yaml")) -> None:
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        super().__init__(data)
