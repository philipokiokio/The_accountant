from accountant.root.utils.abstract_schema import AbstractModel, Currency
from enum import Enum
from typing import Optional, Union
from uuid import UUID
from datetime import datetime, date
from pydantic import conint, condecimal, EmailStr


class InvestmentClass(str, Enum):
    low = "LOW_RISK"
    mid = "MEDIUM_RISK"
    high = "HIGH_RISK"


class TransactionType(str, Enum):
    debit = "DEBIT"
    credit = "CREDIT"


class InvestmentTracker(AbstractModel):
    amount: condecimal(ge=0)
    currency: Currency
    transaction_type: TransactionType


class InvestmentTrackerProfile(InvestmentTracker):
    uid: UUID
    investment_uid: UUID
    date_created_utc: datetime


class PaginatedInvestmentTrackerProfile(AbstractModel):
    result_set: list[InvestmentTrackerProfile] = []
    result_size: conint(ge=0) = 0


class InvestmentTrackerUpdate(AbstractModel):
    amount: Optional[condecimal(ge=0)] = None
    transaction_type: Optional[TransactionType] = None
    currency: Optional[Currency] = None


class Investment(AbstractModel):
    plan_name: str
    return_on_investment: condecimal(ge=0, le=100)
    end_date: date
    nature: InvestmentClass
    is_still_open: bool = True


class InvestmentProfile(Investment):
    investment_uid: UUID
    platform_uid: UUID
    date_created_utc: datetime
    activities: list[InvestmentTrackerProfile] = []


class PaginatedInvestmentProfile(AbstractModel):
    result_set: list[InvestmentProfile] = []
    result_size: conint(ge=0) = 0


class InvestmentUpdate(AbstractModel):
    plan_name: Optional[str] = None
    end_date: Optional[date] = None
    return_on_investment: Optional[condecimal(ge=0, le=100)] = None
    nature: Optional[InvestmentClass] = None
    is_still_open: Optional[bool] = None


class PlatformType(str, Enum):
    app = "APP"
    web = "WEB"
    both = "BOTH"


class PlatformAccessCredential(AbstractModel):
    email: Optional[Union[EmailStr, str]]
    access_username: Optional[str]
    password: str
    transaction_pin: Optional[str]


class Platform(AbstractModel):

    platform_website: str
    name: str
    platform_type: PlatformType
    access_credential: Optional[PlatformAccessCredential] = None


class PlatformProfile(Platform):
    platform_uid: UUID
    user_group_uid: UUID
    date_created_utc: datetime
    investment_plans: list[InvestmentProfile]


class PaginatedPlatformProfile(AbstractModel):
    result_set: list[PlatformProfile] = []
    result_size: conint(ge=0) = 0


class PlatformUpdate(AbstractModel):
    platform_website: Optional[str] = None
    name: Optional[str] = None
    platform_type: Optional[PlatformType] = None
    access_credential: Optional[PlatformAccessCredential] = None
