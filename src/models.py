from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean

# Base Model
Base = declarative_base()


# User Model with fields : id, username, email, password, created_at, updated_at
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return self.username


# #### Magazine

# A magazine that is available for subscription. Includes metadata about the magazine such as the name, description, a base price (for a monthly subscription), and discount - expressed as a decimal - for different subscription plans. The discount for the monthly plan will be set to zero regardless of what is in the discount column in this table. It is possible for a magazine to only offer a subset of plans, in which case the other plans will not be tracked in the database.

# ### Plan

# Plans to which users can subscribe the magazines. The plans contain a title, a description, and a renewal period - expressed in months. Renewal periods CANNOT be zero.

# The plans that your backend should have are:

# 1. Monthly (renewal period = 1 month)
# 2. Quarterly (renewal period = 3 months)
# 3. Half-yearly (renewal period = 6 months)
# 4. Annual (renewal period = 12 months).


class Magazine(Base):
    __tablename__ = "magazines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    base_price = Column(Integer)
    discount_quarterly = Column(Float)
    discount_half_yearly = Column(Float)
    discount_annual = Column(Float)

    def __repr__(self):
        return f"<Magazine {self.name}>"

    def __str__(self):
        return self.name


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    renewal_period = Column(Integer)

    def __repr__(self):
        return f"<Plan {self.title}>"

    def __str__(self):
        return self.title

# A subscription tracks which plan is associated with which magazine for that user. The subscription also tracks the price at renewal for that magazine and the next renewal date. For record keeping purposes, subscriptions are never deleted. If a user cancels a subscription to a magazine, the corresponding `is_active` attribute is set to `False`. Inactive subscriptions are never returned in the response when the user queries their subscriptions.
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    magazine_id = Column(Integer)
    plan_id = Column(Integer)
    price = Column(Float)
    next_renewal_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Subscription {self.id}>"

    def __str__(self):
        return self.id