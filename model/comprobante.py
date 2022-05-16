from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Base64Str, Base64Bytes

class Comprobante(BaseModel):
    estatus: int | None = None
    RFCEmisor: str | None = None
    RFCReceptor: str | None = None
    UUID: str | None = None
    idTipoDocumento: int | None = None
    nombre: str | None = None
    tamanio: int | None = None
    fechaEmision: str  | None = None
    cfdi : str | None = None