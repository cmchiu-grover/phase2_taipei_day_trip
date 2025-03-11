from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Attraction(Base):
    __tablename__ = 'attraction'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(2000), nullable=False)
    address = Column(String(255), nullable=False)
    transport = Column(String(1000), nullable=False)
    rate = Column(Integer, nullable=False, index=True)
    lan = Column(DECIMAL(9, 6), nullable=False)
    lng = Column(DECIMAL(9, 6), nullable=False)
    mrt_id = Column(Integer, ForeignKey("mrt.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False, index=True)


    mrt = relationship("Mrt", back_populates="attractions")
    category = relationship("Category", back_populates="attractions")
    images = relationship("Image", back_populates="attraction")

class Mrt(Base):
    __tablename__ = 'mrt'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)


    attractions = relationship("Attraction", back_populates="mrt")

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)


    attractions = relationship("Attraction", back_populates="category")

class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    attraction_id = Column(Integer, ForeignKey("attraction.id"), nullable=False, index=True)
    url = Column(String(255), nullable=False, index=True)


    attraction = relationship("Attraction", back_populates="images")
