from pydantic import BaseModel

class StatusArchivo(BaseModel):
    codigo: str
    descripcion: str
    descripcionTecnica: str = None
    resultado: bool 

class Archivo(BaseModel):
    tamanio: int