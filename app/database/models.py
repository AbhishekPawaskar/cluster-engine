"""This module is responsible for database modeling & Table creation """

import os
from sqlalchemy import text as sqlalchemy_text
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import FLOAT,TEXT

from .instance import DatabaseInstance

#client instance
db_instance = DatabaseInstance()
Base = db_instance.base

class ClickTable(Base):
    """
    This Class creates the Table Structure required to be present in the Database.
    
    """
    __tablename__ = "click_db"


    id = Column(TEXT, primary_key=True, nullable=False)
    page = Column('page', TEXT)
    x = Column('x',FLOAT)
    y = Column('y',FLOAT)

#Table creation
Base.metadata.create_all(db_instance._engine)

