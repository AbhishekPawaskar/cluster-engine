"""This module is for handling the CRUD operations related to database."""

import sys
import logging
from sqlalchemy.orm import Session
from database.models import ClickTable
from data_models import TableStruct

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] [%(asctime)s.%(msecs)-3d] [api] [%(filename)s:%(funcName)s] [%(message)s]",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout,
                    force=True)


def create_record(db: Session, post: TableStruct):
    """
        This funtion is to create a new record in the Database Table
        Returns: Record ID or None
    """
    try:
        db_post = ClickTable(id=post.id,page=post.page, x=post.x, y=post.y)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        logging.info("ADDED RECORD BEARING ID: "+str(db_post.id))
        return db_post.id

    except Exception as init_ERR:
        logging.error('RECORD CREATION ERROR',exc_info=init_ERR)
        return None