from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional


class AbstractModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


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


class Trend(AbstractModel):
    amount: float
    # percentage_chanage: condecimal(ge=0, le=100) = 0


class DashBoard(AbstractModel):
    summary: Optional[dict[Currency, dict[int, float]]] = None
    yearly_chart: Optional[dict[int, dict[Currency, dict[Month, Trend]]]] = None

    ...
