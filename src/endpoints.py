from fastapi import FastAPI

# create router
from fastapi import APIRouter, Depends, HTTPException, Query
from utils import (
    hash_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from models import User, Magazine, Plan, Subscription
from schemas import (
    UserCreate,
    UserLogin,
    UserResetPassword,
    MagazineBase,
    PlanBase,
    SubscriptionBase,
    SubscriptionCreate,
    NewPassword,
    SubscriptionResponse,
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
    # return the user details with 200 status code along with access token and refresh token
    access_token = create_access_token(data={"sub": user_db.username})
    refresh_token = create_refresh_token(data={"sub": user_db.username})

    # return the user details with 200 status code along with access token and refresh token
    return {
        "user": user_db,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    # return user_db


@router.post("/users/token/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    # generate a new access token
    access_token = create_access_token(data={"sub": current_user.username})
    # generate a new refresh token
    refresh_token = create_refresh_token(data={"sub": current_user.username})
    # return the new access token and refresh token
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# api to reset password by taking email in params
@router.post("/users/reset-password")
def reset_password(email: str = Query(...), db: Session = Depends(get_db)):
    # get the user from the database
    user_db = db.query(User).filter(User.email == email).first()
    # if user not found, return an error with 400 status code
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")
    # set mail to user email
    # return a success message with 200 status code
    return {"msg": "Password reset successful"}


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


@router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# api "/users/deactivate/{username}" to deactivate a user
@router.delete("/users/deactivate/{username}")
def deactivate_user(username: str, db: Session = Depends(get_db)):
    # get the user from the database
    user_db = db.query(User).filter(User.username == username).first()
    # if user not found, return an error with 400 status code
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")
    # delete the user from the database
    db.delete(user_db)
    db.commit()
    # return the user details with 200 status code
    return user_db


# api to get a plan by id
@router.get("/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    # get the plan from the database
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    # if plan not found, return an error with 404 status code
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


# api to get all plans if user is logged in
@router.get("/plans/")
def get_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).all()
    return plans


# api to delete a plan
@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    # get the plan from the database
    plan_db = db.query(Plan).filter(Plan.id == plan_id).first()
    # if plan not found, return an error with 400 status code
    if not plan_db:
        raise HTTPException(status_code=400, detail="Plan not found")
    # delete the plan from the database
    db.delete(plan_db)
    db.commit()
    # return the plan details with 200 status code
    return plan_db


# api to delete all plans
@router.delete("/plans/")
def delete_all_plans(db: Session = Depends(get_db)):
    # get all plans from the database
    plans = db.query(Plan).all()
    # delete all plans from the database
    for plan in plans:
        db.delete(plan)
    db.commit()
    # return the plan details with 200 status code
    return plans


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
    # if renewal period is 0 return an error with 422 status code
    if new_plan.renewal_period == 0:
        raise HTTPException(status_code=422, detail="Renewal period cannot be 0")
    # return the plan details with 201 status code
    return new_plan


# api to update a plan
@router.put("/plans/{plan_id}")
def update_plan(plan_id: int, plan: PlanBase, db: Session = Depends(get_db)):
    # get the plan from the database
    plan_db = db.query(Plan).filter(Plan.id == plan_id).first()
    # if plan not found, return an error with 400 status code
    if not plan_db:
        raise HTTPException(status_code=400, detail="Plan not found")
    # update the plan details
    plan_db.title = plan.title
    plan_db.description = plan.description
    plan_db.renewal_period = plan.renewal_period
    db.commit()
    db.refresh(plan_db)
    # if renewal period is 0 return an error with 422 status code
    if plan_db.renewal_period == 0:
        raise HTTPException(status_code=422, detail="Renewal period cannot be 0")
    # return the plan details with 200 status code
    return plan_db


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


# api to get a magazine by id
@router.get("/magazines/{magazine_id}")
def get_magazine(magazine_id: int, db: Session = Depends(get_db)):
    # get the magazine from the database
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    # if magazine not found, return an error with 404 status code
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    # get the plans available for that magazine using Plan table
    magazine.plans = db.query(Plan).all()
    # and the discount offered for each plan using the discount columns in the Magazine table
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

    return magazine


# api to delete a magazine
@router.delete("/magazines/{magazine_id}")
def delete_magazine(magazine_id: int, db: Session = Depends(get_db)):
    # get the magazine from the database
    magazine_db = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    # if magazine not found, return an error with 404 status code
    if not magazine_db:
        raise HTTPException(status_code=404, detail="Magazine not found")
    # delete the magazine from the database
    db.delete(magazine_db)
    db.commit()
    # return a success message with 200 status code
    return {"msg": "Magazine deleted successfully"}


# api to upadate a magazine
@router.put("/magazines/{magazine_id}")
def update_magazine(
    magazine_id: int, magazine: MagazineBase, db: Session = Depends(get_db)
):
    # get the magazine from the database
    magazine_db = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    # if magazine not found, return an error with 400 status code
    if not magazine_db:
        raise HTTPException(status_code=400, detail="Magazine not found")
    # update the magazine details
    magazine_db.name = magazine.name
    magazine_db.description = magazine.description
    magazine_db.base_price = magazine.base_price
    magazine_db.discount_quarterly = magazine.discount_quarterly
    magazine_db.discount_half_yearly = magazine.discount_half_yearly
    magazine_db.discount_annual = magazine.discount_annual
    db.commit()
    db.refresh(magazine_db)
    # return the magazine details with 200 status code
    return magazine_db


# api to create subscription
@router.post("/subscriptions/", response_model=SubscriptionResponse)
def create_subscription(
    subscription: SubscriptionCreate, db: Session = Depends(get_db)
):
    # Check if user exists
    user = db.query(User).filter(User.id == subscription.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if magazine exists
    magazine = (
        db.query(Magazine).filter(Magazine.id == subscription.magazine_id).first()
    )
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")

    # Check if plan exists
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Create the subscription
    new_subscription = Subscription(
        user_id=subscription.user_id,
        magazine_id=subscription.magazine_id,
        plan_id=subscription.plan_id,
        price=subscription.price,
        next_renewal_date=subscription.next_renewal_date,
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return new_subscription


# api to get all subscriptions
@router.get("/subscriptions/")
def get_subscriptions(db: Session = Depends(get_db)):
    # get all subscriptions from the database
    subscriptions = db.query(Subscription).all()
    return subscriptions


# api to get a subscription by id
@router.get("/subscriptions/{subscription_id}")
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    # get the subscription from the database
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    # if subscription not found, return an error with 404 status code
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


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
        price=subscription.price,
        next_renewal_date=subscription.next_renewal_date,
    )
    new_subscription.is_active = True
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
