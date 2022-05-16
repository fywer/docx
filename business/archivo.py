import logging, sys, hashlib, base64, datetime, os

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class ArchivoService:
    
    def __init__(self,ruta):
        self.__ruta = ruta
        if os.path.isfile(self.__ruta):
            raise Exception(f"El archivo {self.__ruta} existe.")
    
    def getTamanio(self):
        return self._tamanio

    def getRuta(self):
        return self.__ruta
    
    def setArchivo(self, data):
        try:
            with open(self.getRuta(), mode="wb") as f:
                f.write(data)  
                log.info("El archivo ha sido almacenado en {0}".format(self.getRuta()))
            self._tamanio = os.path.getsize(self.getRuta())
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
    
    def deleteArchivo(self, nombre):
        self.__ruta = os.path.join(self.__basepath,nombre)
        if os.path.isfile(self.__ruta):
            os.remove
            log.info("El documento han sido eliminado en disco.")
        else:
            raise Exception("El documento no existe.")            