from datetime import datetime
from enum import Enum
from typing import List

import strawberry
from pydantic import BaseModel, Field

from app.models.chat import ChatType
from app.models.reminder import ReminderType


@strawberry.enum
class RegimenFiscal(Enum):
    NO_DEFINIDO = "No Definido"
    ARRENDAMIENTO = "Arrendamiento"
    SUELDOS_Y_SALARIOS_E_INGRESOS_A_SALARIOS = (
        "Sueldos y Salarios e Ingresos Asimilados a Salarios"
    )
    DEMAS_INGRESOS = "Demás Ingresos"
    PERSONAS_FISICAS_CON_ACTIVIDADES_EMPRESARIALES_Y_PROFESIONALES = (
        "Personas físicas con actividades empresariales y profesionales"
    )
    INGRESOS_POR_DIVIDENDOS = "Ingresos por Dividendos"
    INGRESOS_POR_INTERESES = "Ingresos por Intereses"
    REGIMEN_DE_LOS_INGRESOS_POR_OBTENCION_DE_PREMIOS = (
        "Régimen de los ingresos por obtencion de premios"
    )
    SIN_OBLIGACIONES_FISCALES = "Sin Obligaciones Fiscales"
    INCORPORACION_FISCAL = "Incorporación Fiscal"
    ACTIVIDADES_AGSP = "Actividades Agrícolas, Silvícolas, Pesqueras y similares"
    RESICO = "Régimen Simplificado de Confianza"
    DLRFPYDLEM = (
        "De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales"
    )
    ENAJENACION_DE_ACCIONES_EN_BOLSA_DE_VALORES = (
        "Enajenación de Acciones en Bolsa de Valores"
    )
    RDAECIATDPT = "Régimen de Actividades Empresariales con Ingresos a Través de Plataformas Tecnológicas"
    GENERAL_DE_LEY_PERSONAS_MORALES = "General de Ley Personas Morales"
    PERSONAS_MORALES_CON_FINES_NO_LUCRATIVOS = (
        "Personas Morales con Fines no Lucrativos"
    )
    RDEOADB = "Régimen de enajenación o adquisición de bienes"
    CONSOLIDACION = "Consolidación"
    SOCIEDADES_COOPERATIVAS_DE_PRODUCCION = "Sociedades Cooperativas de Producción"
    OPCIONAL_PARA_GRUPOS_DE_SOCIEDADES = "Opcional para Grupos de Sociedades"
    COORDINADOS = "Coordinados"
    HIDROCARBUROS = "Hidrocarburos"


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
    regimenFiscal: RegimenFiscal
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
