from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Double
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql.base import ColumnSet

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



