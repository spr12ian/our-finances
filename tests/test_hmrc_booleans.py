# test_hmrc_booleans.py

import pytest

from finances.classes.hmrc.booleans import (
    HMRCBooleans,
)


@pytest.fixture
def hmrc_booleans() -> HMRCBooleans:
    return HMRCBooleans()


def test_are_any_of_these_figures_provisional_returns_false(
    hmrc_booleans: HMRCBooleans,
) -> None:
    assert hmrc_booleans.are_any_of_these_figures_provisional() is False


def test_are_computations_provided_returns_false(hmrc_booleans: HMRCBooleans) -> None:
    assert hmrc_booleans.are_computations_provided() is False
