import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, os.path.join(grandparent_dir, 'Backend', 'src'))

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from database import Base, get_db

# テスト用の環境変数を設定する
os.environ["TESTING"] = "True"

# テスト用のデータベースセッションを作成する
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def test_get_db():
    db = next(override_get_db())
    assert db is not None
    assert isinstance(db, Session)

def test_database_connection():
    db = next(override_get_db())
    assert db.bind.name == "sqlite"
    assert db.bind.url.database == ":memory:"

def test_create_tables():
    db = next(override_get_db())
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    
    assert "orders" in tables
    assert "inventories" in tables
    assert "allocation_results" in tables

def test_database_connection_failure():
    INVALID_DATABASE_URL = "sqlite:///invalid.db"
    with pytest.raises(SQLAlchemyError):
        engine = create_engine(INVALID_DATABASE_URL)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = TestingSessionLocal()
        inspector = inspect(db.bind)

def test_create_tables_failure():
    class InvalidBase:
        pass

    with pytest.raises(SQLAlchemyError):
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        InvalidBase.metadata.create_all(bind=engine)
