# importing the required libraries
import hashlib


# function to hash a password
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# function to verify a password
def verify_password(plain_password: str, hashed_password: str):
    return hash_password(plain_password) == hashed_password
