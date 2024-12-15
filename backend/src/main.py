import asyncio
import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi import security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient


security = HTTPBearer()


load_dotenv()

app = FastAPI()


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://maang-stocks.vercel.app"  # Production React domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MONGO_URL = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HEADER_1')}.lubr6.mongodb.net/?retryWrites=true&w=majority&appName={os.getenv('DB_HEADER_2')}"
client = AsyncIOMotorClient(MONGO_URL)
db = client[os.getenv("DB_NAME")]

async def fetch_stock_data():
    stock_data = {}

    async def process_stock(name):
        collection = db[name]
        cursor = collection.find({}, {"_id": 0, "symbol": 1, "price": 1, "percentageChange": 1}).limit(10)
        async for doc in cursor:
            stock_data[name] = {
                "symbol": doc["symbol"],
                "price": doc["price"],
                "percentageChange": abs(float(doc["percentageChange"])),
                "down": float(doc["percentageChange"]) < 0
            }

    # Process all collections concurrently
    await asyncio.gather(*(process_stock(name) for name in ["meta", "amazon", "apple", "netflix", "google"]))

    return stock_data

@app.get("/stocks")
async def get_stocks(authenticated: dict = Depends(authenticate_token)):
    try:
        stock_data = await fetch_stock_data()
        return {"stock_data": stock_data}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

