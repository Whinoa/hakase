from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound
from lib.models import Base, session

class Note(Base):
  __tablename__ = 'notes'

  key = Column(String(100), primary_key=True)
  content = Column(String(500), nullable=False)
  
  def find(self, key):
    try:
      note = session.query(Note).filter_by(key = key).one()
      return note 
    except NoResultFound:
      return False

  def add(self, key, content):
    note = Note(key=key, content=content)
    session.add(note)
    session.commit()

  def __str__(self):
    return self.content