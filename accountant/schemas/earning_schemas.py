from accountant.root.utils.abstract_schema import AbstractModel
from pydantic import condecimal, conint
from enum import Enum
from datetime import date, datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal


class Currency(str, Enum):
    naira = "Naira"
    dollars = "Dollars"
    pounds = "Pounds"
    euros = "Euros"


class Month(str, Enum):
    jan = "January"
    feb = "February"
    mar = "March"
    apr = "April"
    may = "May"
    jun = "June"
    jul = "July"
    aug = "August"
    sept = "September"
    oct = "October"
    nov = "November"
    dec = "December"

    ...


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


class TrendEarning(AbstractModel):
    amount: float
    # percentage_chanage: condecimal(ge=0, le=100) = 0


class EarningDashBoard(AbstractModel):
    summary: Optional[dict[Currency, dict[int, float]]] = None
    yearly_chart: Optional[dict[int, dict[Currency, dict[Month, TrendEarning]]]] = None

    ...
