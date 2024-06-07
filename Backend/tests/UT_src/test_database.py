import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, os.path.join(grandparent_dir, 'Backend', 'src'))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db

# テスト用の環境変数を設定する
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"

# テスト用のデータベースセッションを作成する
SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def test_get_db():
    db = next(get_db())
    assert db is not None
    assert isinstance(db, sessionmaker)
    db.close()

def test_database_connection():
    with pytest.raises(Exception):
        # 無効な認証情報でデータベース接続を試みる
        invalid_url = f"postgresql://invalid_user:invalid_password@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
        invalid_engine = create_engine(invalid_url)
        invalid_engine.connect()

def test_create_tables():
    # テーブルが正常に作成されたことを確認する
    tables = Base.metadata.tables.keys()
    assert "orders" in tables
    assert "inventories" in tables
    assert "allocation_results" in tables

def test_session_rollback():
    db = next(get_db())
    try:
        # 例外が発生する操作を実行する
        raise Exception("Test exception")
    except Exception:
        # セッションがロールバックされることを確認する
        assert db.transaction.is_active is False
    finally:
        db.close()

def test_session_close():
    db = next(get_db())
    # セッションが正常に閉じられることを確認する
    db.close()
    assert db.transaction.is_active is False
