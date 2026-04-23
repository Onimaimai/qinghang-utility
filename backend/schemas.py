from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    pushplus_token: Optional[str] = None
    balance_threshold: float
    water_balance_threshold: float = 30.0
    created_at: datetime
    has_credential: bool = False

    class Config:
        from_attributes = True


class CredentialCreate(BaseModel):
    pms_account: str
    pms_password: str


class CredentialResponse(BaseModel):
    id: int
    pms_account: str
    room_info: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    pushplus_token: Optional[str] = None
    balance_threshold: Optional[float] = None
    water_balance_threshold: Optional[float] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class BalanceResponse(BaseModel):
    balance: float
    crawled_at: datetime


class DetailItem(BaseModel):
    date: str
    type: str
    amount: float
    balance: float
    remark: Optional[str] = None


class EnergyRecord(BaseModel):
    date: str
    electricity: Optional[float] = None
    water: Optional[float] = None
