from abc import ABC, abstractmethod
from util.conexion import SQLServer
# from interface.documento import IDocumentoData
import logging, sys
from datetime import date, datetime

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
        self.__db = SQLServer()
        try:
            self.__cursor = self.__db.cursor()
        except Exception as e:
            log.warn(f"DATA: {e}\n")
            raise Exception("{0}".format(e))
    
    def __getEntity(self):
        return self.__cursor

    def doInsert(self, documento):
        sqlquery = f"INSERT INTO t_documento (estatus, RFCEmisor, RFCReceptor, UUID, idTipoDocumento, nombre, tamanio, fechaEmision) " 
        sqlquery += f'''VALUES ('{documento['estatus']}',
        '{documento['RFCEmisor']}',
        '{documento['RFCReceptor']}', 
        '{documento['UUID']}', 
        '{documento['idTipoDocumento']}', 
        '{documento['nombre']}', 
        '{documento['tamanio']}', 
        '{datetime.now().strftime( '%Y-%m-%dT%H:%M:%S' ) }');'''
        try:
            log.info(sqlquery)
            self.__getEntity().execute(sqlquery)
            self.__getEntity().commit()
        except Exception as e:
            raise Exception("DATA: {0}".format(e))

    def doDelete(self, id):
        sqlquery = f"DELETE FROM t_documento WHERE id = {id};"
        try:
            log.info(sqlquery)
            self.__getEntity().execute(sqlquery)
            self.__getEntity().commit()
        except Exception as e:
            raise Exception("DATA: {0}".format(e))
    
    def doSelect(self, id=False):
        if id == False:
            sqlquery = f"SELECT * FROM Documento ORDER BY fecha DESC;"
            try:
                log.info(sqlquery)
                self.__getEntity().execute(sqlquery)
                rows = self.__getEntity().fetchall()
                documentos = list()
                for data in rows:
                    documento = {
                        'id' : data[0],
                        'nombre' : data[1],
                        'tipo' : data[2],
                        'tamanio': data[3],
                        'fecha' : data[4].isoformat(),                     
                        'ruta' : data[5],
                    }
                    documentos.append(documento)
                return documentos
            except Exception as e:
                log.warn(f"DATA: {e}\n")
                raise Exception("Han ocurrido excepciones en el repositorio.")
        else:
            sqlquery = f"SELECT * FROM t_documento WHERE id='{int(id)}';"
            try:
                log.info(sqlquery)
                self.__getEntity().execute(sqlquery)
                data = self.__getEntity().fetchone()
                
                if  data != None:
                    return {
                        'id' : data[0],
                        'nombre' : data[1],
                        'tipo' : data[2],
                        'tamanio': data[3],
                        'fecha' : data[4].isoformat(),                     
                        'ruta' : data[5],
                    }
                else:
                    return False
            except Exception as e:
                log.warn(f"DATA: {e}\n")
                
                raise Exception("DATA: {0}".format(e))

    def findByType(self, tipo):
        sqlquery = f"SELECT * FROM t_documento WHERE tipo='{tipo}';"
        try:
            log.info(sqlquery)
            self.__getEntity().execute(sqlquery)
            rows = self.__getEntity().fetchall()
            documentos = list()
            for row in rows:
                documentos.append(Documento(row))
            return documentos
        except Exception as e:
            raise Exception(e)

    def findByDate(self, inicio, final):
        i = date.fromisoformat(inicio)
        f = date.fromisoformat(final)
        diainicio, mesinicio, anioinicio = i.day, i.month, i.year
        diafinal, mesfinal, aniofinal = f.day, f.month, f.year
        sqlquery = f'''SELECT * FROM t_documento WHERE 
        ( YEAR(fecha) >= {anioinicio} AND YEAR(fecha) <= {aniofinal} ) 
        AND ( MONTH(fecha) >= {mesinicio} AND MONTH(fecha) <= {mesfinal} ) 
        AND ( DAY(fecha) >= {diainicio} AND DAY(fecha) <= {diafinal} )'''
        try:
            log.info(sqlquery)
            self.__getEntity().execute(sqlquery)
            rows = self.__getEntity().fetchall()
            documentos = list()
            for row in rows:
                documentos.append(Documento(row))
            return documentos
        except Exception as e:
            raise Exception(e)