from util.conexion import MySQL
from data.documento import IDocumentoData
from model.comprobante import Documento
import logging, sys

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class ArchivoRepostory(IDocumentoData):
    def __init__(self):
        self.__db = MySQL()
        try:
            self.__cursor = self.__db.cursor()
        except Exception as e:
            raise Exception(e)

    def __getEntity(self):
        return self.__cursor    

    def doInsert(self, documento):
        sqlquery = f"INSERT INTO t_documento (documento) " 
        sqlquery += f"VALUES ('{documento}');"
        try:
            self.__getEntity().execute(sqlquery)
            self.__getEntity().commit()
            log.info(sqlquery)
        except Exception  as e:
            raise Exception(e)

    def doDelete(self, id):
        sqlquery = f"DELETE FROM t_documento WHERE id = {id};"
        try:
            self.__getEntity().execute(sqlquery)
            self.__getEntity().commit()
        except Exception as e:
            raise Exception(e)

    def doSelect(self, id=False):
        if id != False:
            sqlquery = f"SELECT * FROM t_documento WHERE id='{id}';"
            try:
                log.info(sqlquery)
                self.__getEntity().execute(sqlquery)
                row = self.__getEntity().fetchone()
                return Documento(row)
            except Exception as e:
                return Exception(e)
        else:
            return

    def max(self):
        sqllast = f"SELECT MAX(id) FROM t_documento;" 
        try:
            self.__getEntity().execute(sqllast)
            log.info(sqllast)
            max = self.__getEntity().fetchone()
            return max[0]
        except Exception as e:
            return Exception(e)