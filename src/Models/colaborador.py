from database import Base
from sqlalchemy import Column, Integer , String, ForeignKey
from sqlalchemy.orm import relationship
from Models.persona import persona

class colaborador(Base):
    __tablename__ = 'colaborador'
    
    id = Column(Integer, primary_key=True, index=True)
    dedicacion =Column (String)
    telefone =Column (String)
    persona_id = Column(Integer, ForeignKey('persona.id'))
    
    persona = relationship("persona", back_populates="colaborador")
    