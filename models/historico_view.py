# app/models/historico_view.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from models.auth_user import Base

class VerHistoricoIncidente(Base):
    __tablename__ = "ver_Historico_Incidentes"

    id = Column(Integer, primary_key=True)
    cc_usuario = Column(String(50))  # La cédula puede venir como string o int, usamos string por seguridad
    tipo_incidente = Column(String)
    incidente = Column(String)
    municipio = Column(String)
    sector = Column(String, nullable=True)
    prioridad = Column(String)
    estado = Column(String)
    descripcion = Column(String)
    fecha_hora = Column(DateTime)
    ubicacion = Column(JSON)
    evidencias = Column(JSON)