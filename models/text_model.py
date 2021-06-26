from sqlalchemy import Column
import sqlalchemy
from AR_Copy_Paste.dependencies import Base

class TextDB(Base):

    __tablename__ = 'text'

    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    data = Column(sqlalchemy.String)
