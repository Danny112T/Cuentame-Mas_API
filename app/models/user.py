from datetime import datetime
from enum import Enum
from typing import List

import strawberry
from pydantic import BaseModel, Field

from app.models.chat import ChatType
from app.models.reminder import ReminderType


@strawberry.enum
class RegimenFiscal(Enum):
    NO_DEFINIDO = "NO_DEFINIDO"
    ARRENDAMIENTO = "ARRENDAMIENTO"
    SUELDOS_Y_SALARIOS = "SUELDOS_Y_SALARIOS"
    DEMAS_INGRESOS = "DEMAS_INGRESOS"
    ACTIVIDADES_EMPRESARIALES = "ACTIVIDADES_EMPRESARIALES"
    DIVIDENDOS = "DIVIDENDOS"
    INTERESES = "INTERESES"
    PREMIOS = "PREMIOS"
    SIN_OBLIGACIONES = "SIN_OBLIGACIONES"
    INCORPORACION_FISCAL = "INCORPORACION_FISCAL"
    ACTIVIDADES_AGSP = "ACTIVIDADES_AGSP"
    RESICO = "RESICO"
    REGIMENES_PREFERENTES = "REGIMENES_PREFERENTES"
    ENAJENACION_ACCIONES = "ENAJENACION_ACCIONES"
    PLATAFORMAS_TECNOLOGICAS = "PLATAFORMAS_TECNOLOGICAS"
    PERSONAS_MORALES = "PERSONAS_MORALES"
    SIN_FINES_LUCRO = "SIN_FINES_LUCRO"
    ENAJENACION_BIENES = "ENAJENACION_BIENES"
    CONSOLIDACION = "CONSOLIDACION"
    COOPERATIVAS = "COOPERATIVAS"
    GRUPOS_SOCIEDADES = "GRUPOS_SOCIEDADES"
    COORDINADOS = "COORDINADOS"
    HIDROCARBUROS = "HIDROCARBUROS"


REGIMEN_FISCAL_DESCRIPTIONS = {
    RegimenFiscal.NO_DEFINIDO: "No Definido",
    RegimenFiscal.ARRENDAMIENTO: "Arrendamiento",
    RegimenFiscal.SUELDOS_Y_SALARIOS: "Sueldos y Salarios e Ingresos Asimilados a Salarios",
    RegimenFiscal.DEMAS_INGRESOS: "Demás Ingresos",
    RegimenFiscal.ACTIVIDADES_EMPRESARIALES: "Personas físicas con actividades empresariales y profesionales",
    RegimenFiscal.DIVIDENDOS: "Ingresos por Dividendos",
    RegimenFiscal.INTERESES: "Ingresos por Intereses",
    RegimenFiscal.PREMIOS: "Régimen de los ingresos por obtencion de premios",
    RegimenFiscal.SIN_OBLIGACIONES: "Sin Obligaciones Fiscales",
    RegimenFiscal.INCORPORACION_FISCAL: "Incorporación Fiscal",
    RegimenFiscal.ACTIVIDADES_AGSP: "Actividades Agrícolas, Silvícolas, Pesqueras y similares",
    RegimenFiscal.RESICO: "Régimen Simplificado de Confianza",
    RegimenFiscal.REGIMENES_PREFERENTES: "De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales",
    RegimenFiscal.ENAJENACION_ACCIONES: "Enajenación de Acciones en Bolsa de Valores",
    RegimenFiscal.PLATAFORMAS_TECNOLOGICAS: "Régimen de Actividades Empresariales con Ingresos a Través de Plataformas Tecnológicas",
    RegimenFiscal.PERSONAS_MORALES: "General de Ley Personas Morales",
    RegimenFiscal.SIN_FINES_LUCRO: "Personas Morales con Fines no Lucrativos",
    RegimenFiscal.ENAJENACION_BIENES: "Régimen de enajenación o adquisición de bienes",
    RegimenFiscal.CONSOLIDACION: "Consolidación",
    RegimenFiscal.COOPERATIVAS: "Sociedades Cooperativas de Producción",
    RegimenFiscal.GRUPOS_SOCIEDADES: "Opcional para Grupos de Sociedades",
    RegimenFiscal.COORDINADOS: "Coordinados",
    RegimenFiscal.HIDROCARBUROS: "Hidrocarburos",
}

class User(BaseModel):
    id: str = Field(None, alias="_id")
    name: str
    lastname: str
    email: str
    regimenFiscal: str = RegimenFiscal.NO_DEFINIDO.value
    password: str
    created_at: datetime
    updated_at: datetime | None = None
    reminders: List[str] = []
    chats: List[str] = []

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=User)
class UserType:
    id: strawberry.ID
    name: str
    lastname: str
    email: str
    regimenFiscal: str
    password: str
    created_at: datetime
    updated_at: datetime | None
    reminders: List[ReminderType]
    chats: List[ChatType]


class Token(BaseModel):
    access_token: str
    token_type: str


@strawberry.experimental.pydantic.type(model=Token, all_fields=True)
class TokenType:
    pass
