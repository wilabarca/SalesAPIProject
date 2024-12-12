from sqlalchemy import Column,  Integer, String
from databases import Base


class persona(Base):
    _tablename_= 'persona'
    id = Column (Integer, primary_key=True, index = True)
    name = Column (String, index = True)
    lastaname = Column (String, index = True)
    email = Column ( String, index = True, unique= True)
    password = Column (String , index = True)
    usuario = relationship ("usuario", back_populates="persona")
    colaborador = relationship("colaborador", back_populates="persona", uselist=False)