from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Base64Str, Base64Bytes

class ErrorComprobante(BaseModel):
    codigo: str
    info: str

class Comprobante(BaseModel):
    estatus: int
    RFCEmisor: str
    RFCReceptor: str
    UUID: str
    idTipoDocumento: int
    nombre: str
    tamanio: int
    fechaEmision: str
    cfdi : str = None