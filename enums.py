from enum import Enum


class Region(str, Enum):
    ARICA = "Región de Arica y Parinacota"
    COQUIMBO = "Región de Coquimbo"
    VALPARAISO = "Región de Valparaíso"
    SANTIAGO = "Región Metropolitana de Santiago"
    MAULE = "Región del Maule"
    NUBLE = "Región de Ñuble"
    BIOBIO = "Región del Biobío"
    LA_ARAUCANIA = "Región de La Araucanía"
    LOS_LAGOS = "Región de Los Lagos"


region_dict = {
    1: Region.ARICA,
    2: Region.COQUIMBO,
    3: Region.VALPARAISO,
    4: Region.SANTIAGO,
    5: Region.MAULE,
    6: Region.NUBLE,
    7: Region.BIOBIO,
    8: Region.LA_ARAUCANIA,
    9: Region.LOS_LAGOS
}
