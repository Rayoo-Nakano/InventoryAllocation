from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"  # テーブル名を "orders" に設定

    order_id = Column(String, primary_key=True, index=True)  # 注文IDをプライマリキーに設定
    item_code = Column(String, index=True)  # 商品コード
    quantity = Column(Integer)  # 数量

    allocation_results = relationship("AllocationResult", back_populates="order")  # AllocationResultとのリレーションシップを定義

class Inventory(Base):
    __tablename__ = "inventories"  # テーブル名を "inventories" に設定

    id = Column(Integer, primary_key=True, index=True)  # 在庫IDをプライマリキーに設定
    item_code = Column(String, index=True)  # 商品コード
    quantity = Column(Integer)  # 数量
    receipt_date = Column(Date)  # 入荷日
    unit_price = Column(Float)  # 単価
    created_at = Column(DateTime, default=datetime.utcnow)  # 作成日時を現在の日時に設定

class AllocationResult(Base):
    __tablename__ = "allocation_results"  # テーブル名を "allocation_results" に設定

    id = Column(Integer, primary_key=True, index=True)  # 割当結果IDをプライマリキーに設定
    order_id = Column(String, ForeignKey("orders.order_id"))  # 注文IDを外部キーに設定
    item_code = Column(String, index=True)  # 商品コード
    allocated_quantity = Column(Integer)  # 割当数量
    allocated_price = Column(Float)  # 割当価格
    allocation_date = Column(Date)  # 割当日

    order = relationship("Order", back_populates="allocation_results")  # Orderとのリレーションシップを定義
