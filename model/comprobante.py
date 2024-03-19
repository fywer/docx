from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Base64Str, Base64Bytes

class StatusComprobante(BaseModel):
    codigo: str
    descripcion: str
    descripcionTecnica: str = None
    resultado: bool 

class Comprobante(BaseModel):
    estatus: int
    nombre: str
    
    rfcReceptor: str = None
    rfcEmisor: str = None
    
    cfdiXml : str = None
    cadenaOriginal : str = None
    timbreFiscal : str = None
    sError : str = None
    fechaEmision: str
    idTipoDocumento: str