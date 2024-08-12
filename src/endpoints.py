from fastapi import FastAPI

# create router
from fastapi import APIRouter, Depends, HTTPException
from utils import hash_password
from models import User, Magazine, Plan, Subscription
from schemas import (
    UserCreate,
    UserLogin,
    UserResetPassword,
    MagazineBase,
    PlanBase,
    SubscriptionBase,
    SubscriptionCreate,
)
from database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Add an empty line here


# create a router object
router = APIRouter()


# create an endpoint to say hello world
@router.get("/")
def read_root():
    return {"message": "Hello World"}


# api to register a user using username, email and password
@router.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # create a user in the database
    # if user already exists with same email or username, return an error with 400 status code
    if (
        db.query(User)
        .filter(User.email == user.email or User.username == user.username)
        .first()
    ):
        raise HTTPException(status_code=400, detail="User already exists")
    # create a new user
    new_user = User(
        username=user.username, email=user.email, password=hash_password(user.password)
    )
    # add the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # return the user details with 201 status code
    return (new_user, 201)


# api to login a user using username and password
@router.post("/users/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # get the user from the database
    user_db = (
        db.query(User)
        .filter(
            User.username == user.username,
            User.password == hash_password(user.password),
        )
        .first()
    )
    # if user not found, return an error with 400 status code
    if not user_db:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # return the user details with 200 status code
    return user_db


# api to reset password for a user using email
@router.post("/users/reset-password")
def reset_password(user: UserResetPassword, db: Session = Depends(get_db)):
    # get the user from the database
    user_db = db.query(User).filter(User.email == user.email).first()
    # if user not found, return an error with 400 status code
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")
    # update the password for the user
    user_db.password = hash_password(user.new_password)
    db.commit()
    db.refresh(user_db)
    # return the user details with 200 status code
    return user_db


# api to create magazine
@router.post("/magazines/")
def create_magazine(magazine: MagazineBase, db: Session = Depends(get_db)):
    # create a magazine in the database
    new_magazine = Magazine(
        name=magazine.name,
        description=magazine.description,
        base_price=magazine.base_price,
        discount_quarterly=magazine.discount_quarterly,
        discount_half_yearly=magazine.discount_half_yearly,
        discount_annual=magazine.discount_annual,
    )
    # add the magazine to the database
    db.add(new_magazine)
    db.commit()
    db.refresh(new_magazine)
    # return the magazine details with 201 status code
    return new_magazine


# api to create plan
@router.post("/plans/")
def create_plan(plan: PlanBase, db: Session = Depends(get_db)):
    # create a plan in the database
    new_plan = Plan(
        title=plan.title,
        description=plan.description,
        renewal_period=plan.renewal_period,
    )
    # add the plan to the database
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    # return the plan details with 201 status code
    return new_plan


# api to Retrieve a list of magazines available for subscription. This list should include the plans available for that magazine and the discount offered for each plan.
@router.get("/magazines/")
def get_magazines(db: Session = Depends(get_db)):
    magazines = db.query(Magazine).all()
    # with each magazine, get the plans available for that magazine using Plan table
    # and the discount offered for each plan using the discount columns in the Magazine table    , for monthly it is 0.0
    for magazine in magazines:
        magazine.plans = db.query(Plan).all()
        # calculate the discount for each plan
        for plan in magazine.plans:
            if plan.renewal_period == 1:
                plan.discount = 0.0
            if plan.renewal_period == 3:
                plan.discount = magazine.discount_quarterly or 0.0
            elif plan.renewal_period == 6:
                plan.discount = magazine.discount_half_yearly or 0.0
            elif plan.renewal_period == 12:
                plan.discount = magazine.discount_annual or 0.0

    return magazines


# api to create subscription
@router.post("/subscriptions/")
def create_subscription(
    subscription: SubscriptionCreate, db: Session = Depends(get_db)
):
    # create a subscription in the database
    new_subscription = Subscription(
        user_id=subscription.user_id,
        magazine_id=subscription.magazine_id,
        plan_id=subscription.plan_id,
    )
    new_subscription.is_active = True
    # save new subscription
    # db.add(new_subscription)
    # db.commit()
    # db.refresh(new_subscription)

    # set the start date to the current date
    start_date = datetime.now()

    # set the end date according to the renewal period of the plan

    # get months from plan_id
    # get the plan from the database
    plan_db = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    # get magazine from magazine_id
    # get the magazine from the database
    magazine_db = (
        db.query(Magazine).filter(Magazine.id == subscription.magazine_id).first()
    )
    # if plan not found, return an error with 400 status code
    if not plan_db:
        raise HTTPException(status_code=400, detail="Plan not found")
    # set the end date according to the renewal period of the plan
    new_subscription.next_renewal_date = start_date + relativedelta(
        months=plan_db.renewal_period
    )

    # calculate the amount for the subscription
    # find out discount for the plan from magazine using plan renewal period
    if plan_db.renewal_period == 1:
        new_subscription.price = magazine_db.base_price - (magazine_db.base_price * 0.0)

    if plan_db.renewal_period == 3:
        new_subscription.price = magazine_db.base_price - (
            magazine_db.base_price * magazine_db.discount_quarterly
        )
    elif plan_db.renewal_period == 6:
        new_subscription.price = magazine_db.base_price - (
            magazine_db.base_price * magazine_db.discount_half_yearly
        )
    elif plan_db.renewal_period == 12:
        new_subscription.price = magazine_db.base_price - (
            magazine_db.base_price * magazine_db.discount_annual
        )

    # add the subscription to the database
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    # return the subscription details with 201 status code
    return new_subscription


# api to get all subscriptions for a user
@router.get("/subscriptions/{user_id}")
def get_subscriptions(user_id: int, db: Session = Depends(get_db)):
    # get all active subscriptions for the user
    subscriptions = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.is_active == True)
        .all()
    )
    #
    return subscriptions


# api to modify a subscription
@router.put("/subscriptions/{subscription_id}")
def modify_subscription(
    subscription_id: int,
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
):
    # get the subscription from the database
    # If a user modifies their subscription for a magazine, the corresponsing subsciption is deactivated and a new subscription is created with a new renewal date depending on the plan that is chosen by the user.
    subscription_db = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    # if subscription not found, return an error with 400 status code
    if not subscription_db:
        raise HTTPException(status_code=400, detail="Subscription not found")
    # set the is_active attribute to False
    subscription_db.is_active = False
    db.commit()
    db.refresh(subscription_db)
    # create a new subscription with the new plan
    new_subscription = Subscription(
        user_id=subscription.user_id,
        magazine_id=subscription.magazine_id,
        plan_id=subscription.plan_id,
    )
    new_subscription.is_active = True
    # set the start date to the current date
    start_date = datetime.now()
    # get the plan from the database
    plan_db = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    # get magazine from magazine_id
    # get the magazine from the database
    magazine_db = (
        db.query(Magazine).filter(Magazine.id == subscription.magazine_id).first()
    )
    # if plan not found, return an error with 400 status code
    if not plan_db:
        raise HTTPException(status_code=400, detail="Plan not found")
    # set the end date according to the renewal period of the plan
    new_subscription.next_renewal_date = start_date + relativedelta(
        months=plan_db.renewal_period
    )
    # calculate the amount for the subscription
    # find out discount for the plan from magazine using plan renewal period
    if plan_db.renewal_period == 1:
        new_subscription.price = magazine_db.base_price - (magazine_db.base_price * 0.0)

    if plan_db.renewal_period == 3:
        new_subscription.price = magazine_db.base_price - (
            magazine_db.base_price * magazine_db.discount_quarterly
        )
    elif plan_db.renewal_period == 6:

        new_subscription.price = magazine_db.base_price - (
            magazine_db.base_price * magazine_db.discount_half_yearly
        )
    elif plan_db.renewal_period == 12:
        new_subscription.price = magazine_db.base_price - (
            magazine_db.base_price * magazine_db.discount_annual
        )
    # add the subscription to the database
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    # return the subscription details with 200 status code
    return new_subscription


# api to cancel a subscription
@router.delete("/subscriptions/{subscription_id}")
def cancel_subscription(subscription_id: int, db: Session = Depends(get_db)):
    # get the subscription from the database
    subscription_db = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    # if subscription not found, return an error with 400 status code
    if not subscription_db:
        raise HTTPException(status_code=400, detail="Subscription not found")
    # set the is_active attribute to False
    subscription_db.is_active = False
    db.commit()
    db.refresh(subscription_db)
    # return the subscription details with 200 status code
    return subscription_db
