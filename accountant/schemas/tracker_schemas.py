from pydantic import condecimal, conint

from accountant.root.utils.abstract_schema import (
    AbstractModel,
    Currency,
    Month,
    DashBoard,
)
from typing import Optional
from uuid import UUID
from datetime import datetime


class Tracker(AbstractModel):
    amount: condecimal(ge=0)
    label: str
    description: Optional[str] = None
    currency: Currency


class TrackerExtended(Tracker):
    month: Month
    year: int
    user_uid: UUID


class TrackerProfile(TrackerExtended):
    tracker_uid: UUID
    date_created_utc: datetime


class PaginatedTrackerProfile(AbstractModel):
    result_set: list[TrackerProfile] = []
    result_size: conint(ge=0) = 0


class TrackerUpdate(AbstractModel):
    amount: Optional[condecimal(ge=0)] = None
    label: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[Currency] = None


class TrackingDashBoard(DashBoard): ...
