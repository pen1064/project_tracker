import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


class Database:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set.")

        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.Base = declarative_base()

    def get_db(self) -> Session:
        """
        FastAPI dependency for DB session
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db(self):
        """
        Creates all tables in the db according to models inheriting from Base.
        Call ONCE for initial setup.
        """
        self.Base.metadata.create_all(bind=self.engine)


# Create a single instance for use throughout the app
database = Database()
