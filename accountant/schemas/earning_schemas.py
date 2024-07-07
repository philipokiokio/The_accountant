from accountant.root.utils.abstract_schema import (
    AbstractModel,
    Currency,
    Month,
    DashBoard,
)
from pydantic import condecimal, conint
from datetime import date, datetime
from uuid import UUID
from typing import Optional


class Earning(AbstractModel):
    amount: condecimal(ge=0)
    currency: Currency
    pay_date: date
    month: Month


class EarningUpdate(AbstractModel):
    amount: Optional[condecimal(ge=0)] = None
    currency: Optional[Currency] = None
    pay_date: Optional[date] = None
    month: Optional[Month] = None


class EarningExtended(Earning):
    year: int
    user_uid: UUID


class EarningProfile(EarningExtended):
    amount: float

    earning_uid: UUID
    user_uid: UUID
    date_created_utc: datetime


class PaginatedEarningProfile(AbstractModel):
    result_set: list[EarningProfile] = []
    result_size: conint(ge=0) = 0


class EarningDashBoard(DashBoard): ...
