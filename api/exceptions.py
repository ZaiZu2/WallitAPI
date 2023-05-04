from config import CurrenciesEnum
from datetime import datetime


class RatesUnavailableError(LookupError):
    def __init__(
        self, source: CurrenciesEnum, target: CurrenciesEnum, date: datetime
    ) -> None:
        self.source = source
        self.target = target
        self.date = date

    def __str__(self) -> str:
        return f"{self.source} -> {self.target} on {self.date.date()} rates are not available in the DB"
