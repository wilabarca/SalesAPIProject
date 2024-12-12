from sqlalchemy import Column, Integer ,String, ForeignKey
from sqlalchemy.orm import relationship
from databases import Base
from Models.persona import persona


class usuario (Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index= True)
    username = Column (String, unique=True, index=True)
    password = Column(String)
    persona_id = Column(Integer, ForeignKey('persona.id'))
    
    persona = relationship("persona", back_populates="usuario")
