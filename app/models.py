from fastapi import security
from fastapi.params import Security
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum, Boolean, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy.schema import Index
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.inspection import inspect
from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore, auth_required, hash_password
import uuid

import enum



class ReprMixin:
    def __repr__(self):
        cls_name = self.__class__.__name__
        columns = inspect(self.__class__).columns.keys()
        values = ', '.join(f"{col} = {getattr(self, col)!r}" for col in columns)
        return f'{cls_name} {values}'



class GradeEnum(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5

print(GradeEnum(1))

class GenderEnum(enum.Enum):
    female = 'Женский'
    male = 'Мужской'

class RoleEnum(enum.Enum):
    admin = 'admin'
    user = 'user'



Base = declarative_base(cls=ReprMixin)


class Media(Base, ReprMixin):
    __tablename__ = "media"
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(80))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    


class File(Base, ReprMixin):
    __tablename__ = 'files'

    id = Column(Integer, autoincrement=True, primary_key=True) 
    title = Column(String(50), nullable=True)
    file_path = Column(String, nullable=True)
    file_type = Column(String(50), nullable=True)
    file_extension = Column(String(8), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.now)



class News(Base, ReprMixin):
    __tablename__ = 'news'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey('media.id'))
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True) 

    media = relationship("Media", backref="news_items", lazy='joined') 
    file = relationship("File", backref="news_items", lazy='joined')




class HomeWork(Base, ReprMixin):
    __tablename__ = 'homework'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    media_id = Column(Integer, ForeignKey('media.id'))
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)

    media = relationship("Media", backref="homework_items") 
    file = relationship("File", backref="homework_items") 

    grade = Column(Enum(GradeEnum), name='grade_types') 




class Event(Base, ReprMixin): 
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, ForeignKey('media.id'))
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)

    media = relationship("Media", backref="event_items") 
    file = relationship("File", backref="event_items")    
    start_date = Column(DateTime, index=True) 
    end_date = Column(DateTime)
    members_count = Column(Integer)
    members_id = Column(Integer, ForeignKey("members.candidat_id"), index=True)

    member = relationship("Members", backref="event")

    __table_args__ = (
        Index("idx_members_id", "members_id"),
        Index("idx_start_date", "start_date"),
    )

    

class Members(Base, ReprMixin):
    __tablename__ = 'members'
    candidat_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    first_name = Column(String(30))
    last_name = Column(String(30))

    @hybrid_property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    age = Column(Integer) 
    gender = Column(Enum(GenderEnum), name='gender_types')
    grade = Column(Enum(GradeEnum), name='grade_types')
    school = Column(String)
    portfolio = Column(Text)
    fs_uniquifier = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    description = Column(Text)
    activity = Column(String) 
    email = Column(String, index=True)
    phone_number = Column(String(25))
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)

    __table_args__ = (
        Index("idx_email", "email"),
    )



class Categories(Base, ReprMixin):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50))
    parent_id = Column(Integer, ForeignKey("categories.id")) 
    subclass_name = relationship("Categories", remote_side=[id]) 


class Role(Base, RoleMixin, ReprMixin):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(8), default=RoleEnum.user.value)
    



admin_roles = Table(
    'admin_roles', Base.metadata,
    Column('admin_id', Integer, ForeignKey('admin.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class Admin(Base, UserMixin, ReprMixin):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    fs_uniquifier = Column(String(64), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    phone_number = Column(String(25))

    roles = relationship("Role", secondary=admin_roles, backref="admins", lazy='joined')




