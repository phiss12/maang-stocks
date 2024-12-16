import asyncio
import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi import security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pymongo.server_api import ServerApi
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

security = HTTPBearer()

load_dotenv()

app = FastAPI()
MONGO_URL = f"mongodb+srv://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HEADER_1")}.lubr6.mongodb.net/?retryWrites=true&w=majority&appName={os.getenv("DB_HEADER_2")}"

app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        os.getenv("DEV_ALLOWED_LINK") if bool(os.getenv("DEV_ENV")) else os.getenv("PROD_ALLOWED_LINK")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def authenticate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        results = jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")]
        )
        return results
    except JWTError:
        raise HTTPException(status_code=403, detail="Access forbidden")


@app.get("/stocks")
async def get_stock_data(authenticated: dict = Depends(authenticate_token)):
    try:
        # Use async MongoDB client (Motor)
        client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))
        db = client[os.getenv("DB_NAME")]

        # Fetch all collection names
        collection_names = await db.list_collection_names()
        stock_data = {}

        # Iterate over collections and fetch one document per collection
        for collection_name in collection_names:
            document = await db[collection_name].find_one(
                {}, {"_id": 0, "symbol": 1, "price": 1, "percentageChange": 1}
            )
            if document:
                percentage_change = float(document["percentageChange"])
                stock_data[collection_name] = {
                    "symbol": document["symbol"],
                    "price": document["price"],
                    "percentageChange": abs(percentage_change),
                    "down": percentage_change < 0,
                }

        return JSONResponse(content={"stock_data": stock_data})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
