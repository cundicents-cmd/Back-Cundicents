# app/models/reporte_view.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from models.auth_user import Base

class VerReporte(Base):
    __tablename__ = "ver_Reportes"  # Nombre exacto de tu vista en MySQL

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer)
    usuario = Column(String)
    id_incidente = Column(Integer)
    incidente = Column(String)
    id_municipio = Column(Integer)
    municipio = Column(String)
    id_sector = Column(Integer, nullable=True)
    sector = Column(String, nullable=True)
    id_prioridad = Column(Integer)
    tp_prioridad = Column(String)
    id_estado = Column(Integer)
    estado = Column(String)
    descripcion = Column(String)
    fecha_hora = Column(DateTime)
    ubicacion = Column(JSON)     
    evidencias = Column(JSON) 