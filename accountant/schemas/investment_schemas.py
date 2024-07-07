from accountant.root.utils.abstract_schema import AbstractModel
from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import conint, condecimal


class PlatformType(str, Enum):
    app = "APP"
    web = "WEB"


class PlatformAccessCredential(AbstractModel):
    email: Optional[str]
    access_username: Optional[str]
    password: str
    transaction_pin: Optional[str]


class Platform(AbstractModel):

    platform_website: str
    name: str
    platform_type: PlatformType
    access_credential: PlatformAccessCredential


class PlatformProfile(Platform):
    platform_uid: UUID
    date_created_utc: datetime


class PaginatedProfile(AbstractModel):
    result_set: list[PlatformProfile] = []
    result_size: conint(ge=0) = 0


class PlatformUpdate(AbstractModel):
    platform_website: Optional[str] = None
    name: Optional[str] = None
    platform_type: Optional[PlatformType] = None
    access_credential: Optional[PlatformAccessCredential] = None


class Investment(AbstractModel):

    return_on_investment: condecimal(ge=0, le=100)


class InvestmentClass(str, Enum):
    low = "LOW_RISK"
    mid = "MEDIUM_RISK"
    high = "HIGH_RISK"


class TransactionType(str, Enum):
    debit = "DEBIT"
    credit = "CREDIT"


class InvestmentExtended(Investment):
    nature: InvestmentClass
    is_still_open: bool = True


class InvestmentProfile(InvestmentExtended):
    investment_uid: UUID
    date_created_utc: datetime
    activities: list = []


class PaginatedInvestmentProfile(AbstractModel):
    result_set: list[InvestmentProfile] = []
    result_size: conint(ge=0) = 0


class InvestmentUpdate(AbstractModel):
    return_on_investment: Optional[condecimal(ge=0, le=100)] = None
    nature: Optional[InvestmentClass] = None
    is_still_open: Optional[bool] = None


class InvestmentTracker(AbstractModel):
    amount: condecimal(ge=0)
    transaction_type: TransactionType


class InvestmentTrackerProfile(InvestmentTracker):
    uid: UUID
    investment_uid: UUID
    date_created_utc: datetime


class PaginatedInvestmentTrackerProfile(AbstractModel):
    result_set: list[InvestmentProfile] = []
    result_size: conint(ge=0) = 0


class InvestmentTrackerUpdate(AbstractModel):
    amount: Optional[condecimal(ge=0)] = None
    transaction_type: Optional[TransactionType] = None
