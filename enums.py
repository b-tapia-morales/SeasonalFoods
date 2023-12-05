from enum import Enum
from typing import Dict


class Region(Enum):
    ARICA = "Región de Arica y Parinacota"
    COQUIMBO = "Región de Coquimbo"
    VALPARAISO = "Región de Valparaíso"
    SANTIAGO = "Región Metropolitana de Santiago"
    MAULE = "Región del Maule"
    NUBLE = "Región de Ñuble"
    BIOBIO = "Región del Biobío"
    LA_ARAUCANIA = "Región de La Araucanía"
    LOS_LAGOS = "Región de Los Lagos"


class Zone(Enum):
    NORTE = "Zona Norte"
    CENTRO = "Zona Centro"
    SUR = "Zona Sur"


class Category(Enum):
    FRUTAS = "Frutas"
    HORTALIZAS = "Hortalizas"
    BOVINA = "Carne bovina"
    CARNE = "Carne de cerdo, ave y cordero"
    LACTEOS = "Lácteos, huevos y margarina"
    PAN = "Pan"
    ABARROTES = "Abarrotes y otros"


class BoughtIn(Enum):
    CARNICERIA = "Carnicería"
    PANADERIA = "Panadería"
    FERIA = "Feria libre"
    MINORISTA = "Mercado Minorista"
    MAYORISTA = "Mercado Mayorista"
    SUPERMERCADO = "Supermercado"


region_zone_dict: dict[str, str] = {
    "Región de Arica y Parinacota": "Zona Norte",
    "Región de Coquimbo": "Zona Centro",
    "Región de Valparaíso": "Zona Centro",
    "Región Metropolitana de Santiago": "Zona Centro",
    "Región del Maule": "Zona Centro",
    "Región de Ñuble": "Zona Centro",
    "Región del Biobío": "Zona Centro",
    "Región de La Araucanía": "Zona Sur",
    "Región de Los Lagos": "Zona Sur",
}


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


category_dict = {
    1: Category.FRUTAS,
    2: Category.HORTALIZAS,
    3: Category.BOVINA,
    4: Category.CARNE,
    5: Category.LACTEOS,
    6: Category.PAN,
    7: Category.ABARROTES
}


point_dict = {
    1: BoughtIn.CARNICERIA,
    2: BoughtIn.PANADERIA,
    3: BoughtIn.FERIA,
    4: BoughtIn.MINORISTA,
    5: BoughtIn.MAYORISTA,
    6: BoughtIn.SUPERMERCADO,
}


quality_dict = {
    0: ' ',
    1: 'Primera',
    2: 'Segunda'
}


unit_metric_dict = {
    1: '$/kilo',
    2: '$/bolsa 1 kilo',
    3: '$/envase 1 kilo',
    4: '$/pote 500 gramos',
    5: '$/pan de 250 gramos',
    6: '$/Caja de 1 Litro',
    7: '$/bolsa 800 grs',
    8: '$/bandeja 12 unidades',
    9: '$/unidad',
    10: '$/envase 400 gramos',
    11: '$/botella 900 ml',
    12: '$/kilo (en saco de 5 kilos)',
    13: '$/kilo (en saco de 25 kilos)',
    14: '$/kilo (en envase de 1 kilo)',
    15: '$/bandeja 30 unidades',
    16: '$/envase 125 gramos',
    17: '$/litro'
}
