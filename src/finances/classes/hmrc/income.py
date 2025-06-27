from __future__ import annotations


class HMRCIncome:
    def __init__(self, hmrc: HMRC) -> None:
        self.hmrc = hmrc

    def get_trading_digest(self) -> str:
        return self.hmrc.get_digest_by_type("trading")
