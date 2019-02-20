from sqlalchemy import Column, Integer, String, and_
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from lib.models import Base, girl_tag_association_table, session

from .tag import Tag

import os

tiers = {
    1300: 'Miracle of the Universe',
    1250: 'Princess',
    1200: 'Cinnamon bun',
    1150: 'Miracle',
    1100: 'Blessed',
    1070: 'Lovely',
    1050: 'Cute',
    1020: 'Sempai',
    1000: 'Kouhai',
    950: 'Homely',
    900: 'Childhood friend',
    850: 'Still cute',
    800: 'Kinda cute',
    700: 'Eh',
    0: 'Honorable mention'
}

class QtAnimeGirl(Base):
  __tablename__ = 'girldatabase_qtanimegirl'

  id = Column(Integer, primary_key=True)
  name = Column(String(40), default= '')
  elo = Column(Integer, nullable=False, default= 1000)
  image = Column(String(100), nullable=False, unique= True)

  tags = relationship(
    "Tag",
    secondary = girl_tag_association_table,
    back_populates = "qtanimegirls")

  def __str__(self):
    if self.name is not None and self.name > '':
      return self.name
    else:
      return str(self.id)

  def get_all_girls(self,path='/images/'):
    for path in os.listdir(path):
      a = QtAnimeGirl(image=path)
      session.add(a)
    session.commit()

  def get_new_girls(self,path='/images/'):
    new_girl_count = 0
    for image in os.listdir(path):
      try:
        a = session.query(QtAnimeGirl).filter(QtAnimeGirl.image==image).one()
      except NoResultFound:
        print('Adding new girl with image {}'.format(image))
        a = QtAnimeGirl(image=image)
        session.add(a)
        new_girl_count += 1
    session.commit()
    return new_girl_count

  def get_tier(self):
    elo = self.elo

    while elo not in tiers:
        elo -= 1

    return tiers[elo]

  def get_ranking(self):
      list = session.query(QtAnimeGirl).order_by(QtAnimeGirl.elo.desc()).all()
      return list.index(self) + 1

  def updateELO(self,eloOpponent,score):
    expectedA = 1/(1+pow(10,((eloOpponent-self.elo)/400)))
    self.elo = round(self.elo + 32 * (score-expectedA))
    session.commit()

  def addTag(self,tag):
    try:
      tag = session.query(QtAnimeGirl).filter(and_ (QtAnimeGirl.tags.any(tag = tag),QtAnimeGirl.id == self.id)).one()
    except NoResultFound:
      try:
        new_tag = session.query(Tag).filter(Tag.tag == tag).one()
      except NoResultFound:
        new_tag = Tag(tag=tag)
        session.add(new_tag)
      self.tags.append(new_tag)
      session.commit()
