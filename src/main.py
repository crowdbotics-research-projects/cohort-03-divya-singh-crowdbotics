# import fastapi
from fastapi import FastAPI

# import the endpoints module
import endpoints

# Create an instance of FastAPI
app = FastAPI()

# include the endpoint router
app.include_router(endpoints.router)
