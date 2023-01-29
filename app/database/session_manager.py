"""This Module bears the responsibility of session management"""

from database.models import db_instance

def safe_session():
    """Provide a transactional scope around a series of operations."""
    session = db_instance.initialize_session()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()