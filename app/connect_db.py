
from app.models import Members,Media, File, News,Categories, Event, HomeWork, Base, GenderEnum, GradeEnum
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, select



load_dotenv(find_dotenv())
URL = os.getenv('URL')
engine = create_engine(URL, echo=True)


db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))


Base.query = db_session.query_property()

def init_db():
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    init_db()