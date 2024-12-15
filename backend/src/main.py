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
        "https://maang-stocks.vercel.app",  
        # "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MONGO_URL = f"mongodb+srv://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HEADER_1")}.lubr6.mongodb.net/?retryWrites=true&w=majority&appName={os.getenv("DB_HEADER_2")}"
client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
db = client[os.getenv("DB_NAME")]



@app.get("/stocks")
async def get_stock_data(authenticated: dict = Depends(authenticate_token)):
    try:
        stock_data = {}
        for name in ["meta", "amazon", "apple", "netflix", "google"]:
            collection = db[name]
            documents = collection.find({}, {"_id": 0, "symbol": 1, "price": 1, "percentageChange": 1})
            # Store each document in the dictionary
            for doc in documents:
                if float(doc["percentageChange"]) < 0:
                    down = True
                else:
                    down = False
                stock_data[name] = {
                    "symbol" : doc["symbol"],
                    "price": doc["price"],
                    "percentageChange": abs(float(doc["percentageChange"])),
                    "down" : down
                }
        return {"stock_data": stock_data}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


"""stock_data = {}
        for name in ["meta", "amazon", "apple", "netflix", "google"]:
            collection = db[name]
            documents = collection.find({}, {"_id": 0, "symbol": 1, "price": 1, "percentageChange": 1})
            # Store each document in the dictionary
            for doc in documents:
                if float(doc["percentageChange"]) < 0:
                    down = True
                else:
                    down = False
                stock_data[name] = {
                    "symbol" : doc["symbol"],
                    "price": doc["price"],
                    "percentageChange": abs(float(doc["percentageChange"])),
                    "down" : down
                }"""