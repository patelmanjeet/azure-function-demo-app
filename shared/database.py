from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()

class FileStatus(Base):
    __tablename__ = 'file_status'

    id = Column(Integer, primary_key=True)
    session_id = Column(String(50))
    file_name = Column(String(255))
    status = Column(String(50))

    def __init__(self, session_id, file_name, status):
        self.session_id = session_id
        self.file_name = file_name
        self.status = status

class Database:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        self.session = sessionmaker(bind=self.engine)

    def create_database(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.session()