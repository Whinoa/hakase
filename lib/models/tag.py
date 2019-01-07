from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from lib.models import Base, girl_tag_association_table

class Tag(Base):
  __tablename__ = 'girldatabase_tag'

  id = Column(Integer, primary_key=True)
  tag = Column(String(50), nullable=False)

  qtanimegirls = relationship(
    "QtAnimeGirl",
    secondary = girl_tag_association_table,
    back_populates = "tags")

  def __str__(self):
    return self.tag
