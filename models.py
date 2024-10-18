# ORM 모델 클래스 정의
from sqlalchemy import Boolean, Column, Float, Integer, String, Text
from database import Base


class Sales(Base):
    __tablename__ = 'sales'  # 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True)
    sales_amount = Column(Float, nullable=False)  # 매출액
    month = Column(String(2), nullable=False)  # 월

# todos 테이블
class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    task = Column(Text)
    completed = Column(Boolean, default=False)