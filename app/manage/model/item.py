from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class ItemCategory(Base):
    """비품 카테고리 (우산/보조배터리 등)"""
    __tablename__ = "item_category"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=False)
    deposit_required = Column(Integer, nullable=False, default=0)

    # relationship
    items = relationship("Item", back_populates="category")


class Item(Base):
    """비품 (우산, 보조배터리 등)"""
    __tablename__ = "item"
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("item_category.category_id"), nullable=False)
    serial_no = Column(String(50), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default="AVAILABLE")
    # status: AVAILABLE, RENTED, RESERVED, BROKEN 등

    # relationship
    category = relationship("ItemCategory", back_populates="items")

