from sqlalchemy import create_engine, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///db.sqlite3')
DBSession = sessionmaker(bind=engine)
session = DBSession()
Base = declarative_base()
metadata = Base.metadata

girl_tag_association_table = Table('girldatabase_qtanimegirl_tags',Base.metadata,
  Column('qtanimegirl_id', Integer, ForeignKey('girldatabase_qtanimegirl.id'), nullable=False, index=True),
  Column('tag_id', Integer, ForeignKey('girldatabase_tag.id'), nullable=False, index=True)
)

from .qt_anime_girl import QtAnimeGirl
from .tag import Tag
from .note import Note

metadata.create_all(engine)
