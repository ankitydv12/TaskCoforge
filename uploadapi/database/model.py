from datetime import UTC , datetime 

from sqlalchemy import String , Integer , Text , DateTime , ForeignKey
from sqlalchemy.orm import Mapped , mapped_column , relationship 

from database import Base

class ChatSession(Base):
    __tablename__ = "chat_session"
    session_id:Mapped[String] = mapped_column(String , primary_key=True,index=True)
    created_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True),default=lambda : datetime.now(UTC))

class ChatMessage(Base):
    __tablename__ = "chat_message"
    id : Mapped[Integer] = mapped_column(Integer,primary_key=True, index=True, autoincrement=True)
    session_id : Mapped[String] = mapped_column(ForeignKey("chat_session.session_id") , nullable =False,index=True )
    role:Mapped[String] = mapped_column(String,nullable=False)
    message : Mapped[Text] = mapped_column(Text,nullable=False)
    created_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True),default=lambda : datetime.now(UTC))