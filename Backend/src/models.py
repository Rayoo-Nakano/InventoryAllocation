from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    item_code = Column(String, index=True)
    quantity = Column(Integer)

    allocation_results = relationship("AllocationResult", back_populates="order")

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, index=True)
    quantity = Column(Integer)
    receipt_date = Column(Date)
    unit_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)  # 追加

class AllocationResult(Base):
    __tablename__ = "allocation_results"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"))
    item_code = Column(String, index=True)
    allocated_quantity = Column(Integer)
    allocated_price = Column(Float)
    allocation_date = Column(Date)

    order = relationship("Order", back_populates="allocation_results")