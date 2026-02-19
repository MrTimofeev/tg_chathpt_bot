from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .session import Base


class Dialog(Base):
    """Модель диалога пользователя"""
    __tablename__ = "dialogs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    messages = Column(Text, nullable=False, default='[]')
    
    
    def __repr__(self) -> str:
        return f"<Dialog(user_id={self.user_id})>"
    
    