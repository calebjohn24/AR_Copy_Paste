from sqlalchemy import Column
import sqlalchemy
from AR_Copy_Paste.dependencies import Base

class ImageDB(Base):

    __tablename__ = 'image'

    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    filename = Column(sqlalchemy.String)
