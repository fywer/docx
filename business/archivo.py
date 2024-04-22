import logging, sys, base64, os
from pydantic import BaseModel

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class StatusArchivo(BaseModel):
    codigo: str
    descripcion: str
    descripcionTecnica: str = None
    resultado: bool 

class Archivo(BaseModel):
    tamanio: int

class ArchivoServiceError(Exception):
    def __init__(self, mensaje="Ocurrió un error."):
            self.mensaje = mensaje
            super().__init__(self.mensaje)

class ArchivoService:
    def __init__(self,ruta):
        self.__ruta = ruta
        
    def getTamanio(self):
        return self._tamanio

    def getRuta(self):
        return self.__ruta
    
    def setArchivo(self, data):
        if os.path.isfile(self.__ruta):
            sts = StatusArchivo(**{'codigo':'099','descripcion' : f"El archivo {self.__ruta} existe.", 'descripcionTecnica':'', 'resultado':False })
            raise ArchivoServiceError(sts.dict())
        else:
            try:
                rutaArchivo = self.getRuta()
                with open(rutaArchivo, mode="wb") as f:
                    cleanedBytes = data.replace(b'\r', b'').replace(b'\n', b'')
                    f.write(cleanedBytes)  
                    log.info("El archivo ha sido almacenado en {0}".format(rutaArchivo))
                self._tamanio = os.path.getsize(rutaArchivo)
            except Exception as e:
                raise Exception(e)

    def getAllArchivos(self):
        pass

    def getArchivo(self):
        self.__ruta = os.path.join(self.getRuta())
        with open(self.getRuta(), "rb") as f:
            binarios = f.read()
    
        archivo = base64.b64encode(binarios)
        return archivo.decode('ISO-8859-1')
    
    def deleteArchivo(self):
        try:
            self.__ruta = os.path.join(self.getRuta())
            if os.path.isfile(self.__ruta):
                os.remove(self.__ruta)
                if os.path.isfile(f"{self.__ruta}.xml"):
                    os.remove(f"{self.__ruta}.xml")
                else:
                    raise ArchivoServiceError("El documento XML no existe.")
                log.info("El documento han sido eliminado en disco.")
            else:
                raise ArchivoServiceError("El documento no existe.")
        except Exception as e:
            raise Exception(e)