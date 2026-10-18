# app/models/incidente.py
from sqlalchemy import Column, Integer, String
from models.base import Base


class Incidente(Base):
    __tablename__ = "incidentes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incidente = Column(String(255), nullable=False)
    id_tp_incidente = Column(Integer, nullable=False)
    id_prioridad = Column(Integer, nullable=False)