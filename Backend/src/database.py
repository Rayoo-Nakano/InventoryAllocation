from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# テスト用の環境変数ファイルを読み込む
load_dotenv(".env.test")

print("Environment variables loaded from .env.test:")
print(f"DB_HOST: {os.environ.get('DB_HOST')}")
print(f"DB_PORT: {os.environ.get('DB_PORT')}")
print(f"DB_NAME: {os.environ.get('DB_NAME')}")
print(f"DB_USER: {os.environ.get('DB_USER')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD')}")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT")) if os.environ.get("DB_PORT") else None
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
