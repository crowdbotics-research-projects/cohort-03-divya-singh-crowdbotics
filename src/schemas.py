# importing required modules
from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime


# pydantic schema for UserCreate
class UserCreate(BaseModel):
    username: str
    # email: str
    email: EmailStr
    password: str


# schema for User login : with username and password
class UserLogin(BaseModel):
    username: str
    password: str


# schema for User password reset : with email, new password
class UserResetPassword(BaseModel):
    email: str

class NewPassword(BaseModel):
    new_password: str


# schema for Magazine
class MagazineBase(BaseModel):
    name: str
    description: str
    base_price: float
    discount_quarterly: Optional[float] = None
    discount_half_yearly: Optional[float] = None
    discount_annual: Optional[float] = None


# schema for plan
class PlanBase(BaseModel):
    title: str
    description: str
    renewal_period: int


# schema for subscription
class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    next_renewal_date: str
    price: float


# schema for subscription create
class SubscriptionCreate(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    price: float
    # next_renewal_date: str
    next_renewal_date: datetime.date


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    magazine_id: int
    plan_id: int
    price: float
    next_renewal_date: datetime.date
    is_active: bool

    class Config:
        orm_mode = True