from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# TODO: シークレットマネージャへの移行が完了したら、.env.testファイルの読み込みを削除してください
# .env.testファイルのパスを設定する
env_file_path = os.path.join(os.path.dirname(__file__), ".env.test")

# .env.testファイルが存在するかチェックする
if not os.path.exists(env_file_path):
    raise FileNotFoundError(f"Environment file {env_file_path} not found.")

# .env.testファイルを読み込む
load_dotenv(env_file_path)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# TODO: 本番環境では、TestingSessionLocalを削除してください
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
