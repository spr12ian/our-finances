import os

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from finances.classes.config import Config, ConfigError


@pytest.fixture
def mock_environ(monkeypatch: MonkeyPatch) -> dict[str, str]:
    """Fixture to replace os.environ with mock data."""
    env: dict[str, str] = {
        "APP_ENV": "development",
        "DEBUG": "true",
        "SECRET_KEY": "abc123",
        "APP_PORT": "8080",
    }
    monkeypatch.setattr(os, "environ", env)
    return env


def test_getattr_returns_value(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    assert config.APP_ENV == "development"
    assert config.DEBUG == "true"


def test_getattr_raises_config_error(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    with pytest.raises(ConfigError, match="Environment variable 'MISSING' not found"):
        _ = config.MISSING


def test_repr(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    expected: str = f"<Config with {len(mock_environ)} environment variables>"
    assert repr(config) == expected


def test_dump_prints_filtered_output(
    mock_environ: dict[str, str], capsys: CaptureFixture[str]
) -> None:
    config: Config = Config()
    config.dump("APP_")
    captured: str = capsys.readouterr().out
    assert "APP_ENV=development" in captured
    assert "APP_PORT=8080" in captured
    assert "DEBUG=true" not in captured


def test_filter_by_prefix(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    result: dict[str, str] = config.filter_by_prefix("APP_")
    expected: dict[str, str] = {"APP_ENV": "development", "APP_PORT": "8080"}
    assert result == expected


def test_get_existing_variable(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    assert config.get("SECRET_KEY") == "abc123"


def test_get_with_default(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    assert config.get("MISSING_KEY", default="fallback") == "fallback"


def test_get_raises_if_missing_and_no_default(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    with pytest.raises(
        ConfigError, match="Environment variable 'MISSING_KEY' not found"
    ):
        config.get("MISSING_KEY")


def test_getOptional(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    assert config.getOptional("SECRET_KEY") == "abc123"
    assert config.getOptional("NON_EXISTENT") is None


def test_has(mock_environ: dict[str, str]) -> None:
    config: Config = Config()
    assert config.has("DEBUG") is True
    assert config.has("NON_EXISTENT") is False
