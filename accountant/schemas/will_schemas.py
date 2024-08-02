from accountant.root.utils.abstract_schema import AbstractModel
from uuid import UUID

from typing import Optional
from datetime import date, datetime
from accountant.schemas.investment_schemas import InvestmentProfile
from pydantic import conint


class Will(AbstractModel):
    invitation_uid: UUID
    assigned_uid: Optional[UUID] = None
    is_claimed: bool = False
    investment_uid: UUID
    owner_uid: UUID


class WillProfile(Will):
    will_uid: UUID
    date_claimed: Optional[date] = None
    date_created_utc: datetime


class WillUpdate(AbstractModel):
    invitation_uid: Optional[UUID] = None
    is_claimed: Optional[bool] = None
    assigned_uid: Optional[UUID] = None
    date_claimed: Optional[date]


class WillExtendedProfile(WillProfile):
    investment: InvestmentProfile


class PaginatedWillProfile(AbstractModel):
    result_set: list[WillExtendedProfile] = []
    result_size: conint(ge=0) = 0
