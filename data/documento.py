from abc import ABC, abstractmethod
from util.conexion import MongoDB
import logging, sys, pymongo

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class IDocumentoData(ABC):

    @abstractmethod
    def doInsert(self, documento):
        pass

    @abstractmethod
    def doDelete(self, id):
        pass

    @abstractmethod
    def doSelect(self, id=False):
        pass

class MetadatoRepository(IDocumentoData):
    def __init__(self):
        try:
            self.__db = MongoDB()
            self.__cursor = self.__db.ifywerz
        except Exception as e:
            log.warn(f"DATA: {e}\n")
            raise Exception("{0}".format(e))
    
    def __getEntity(self):
        return self.__cursor
    
    def findComprobanteByNombre(self, nombre):
        try:
            comprobanteT = self.__getEntity().comprobantes.find_one({"nombre" :nombre})
            log.info(f"Se han encotrado en Atlas: {nombre}")
            return comprobanteT
        except Exception as e:
            raise Exception("DATA: {0}".format(e))
    
    def doInsert(self, comprobante):
        try:
            comp_dict = dict(comprobante)
            id = self.__getEntity().comprobantes.insert_one(comp_dict).inserted_id       
            log.info(f"Se han almacenado en Atlas: {comp_dict['nombre']}")
            return id
        except Exception as e:
            raise Exception("DATA: {0}".format(e))

    def doDelete(self, nombre):
        try:
            c = self.__getEntity().comprobantes.find_one_and_delete({"nombre" :nombre})
            if c is None:
                log.warn(f"No se ha eliminado en Atlas: {nombre}")
                raise Exception("No se ha eliminado registro.")
            else:
                log.info(f"Se han eliminado en Atlas: {nombre}")
                return c
        except Exception as e:
            raise Exception("DATA: {0}".format(e))
    
    def doUpdate(self, comprobante):
        try:
            nombre = comprobante['nombre']
            c = self.__getEntity().comprobantes.find_one_and_update({'nombre' : nombre },{ '$set' : comprobante})
            if c is None:
                log.warn(f"No se ha actualizado en Atlas: {nombre}")
                raise Exception("No se ha encontrado registro.")
            else:
                log.info(f"Se han actualizado en Atlas: {nombre}")
                return self.findComprobanteByNombre(nombre)
        except Exception as e:
            raise Exception("DATA: {0}".format(e))

    def doSelect(self):
        try:
            comprobantes = self.__getEntity().comprobantes.find().sort('fechaEmision', pymongo.DESCENDING)
            return comprobantes
        except Exception as e:
            raise Exception("DATA: {0}".format(e))  