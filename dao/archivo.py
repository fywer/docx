from .conexion import SQLServer, MySQL
import logging, sys

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class ArchivoDAO:
    def __init__(self):
        self.db = MySQL()
        try:
            self.cursor = self.db.cursor()
        except Exception as e:
            raise Exception(e)
            
    def insert(self, documento):
        sqlquery = f"INSERT INTO t_documento (documento) " 
        sqlquery += f"VALUES ('{documento}');"
        self.cursor.execute(sqlquery)
        self.db.commit()
        log.info(sqlquery)
    
    def delete(self, id):
        sqlquery = f"DELETE FROM t_documento WHERE id = {id};"
        self.cursor.execute(sqlquery)
        self.db.commit()

    def select(self, id=False):
        if id != False:
            sqlquery = f"SELECT * FROM t_documento WHERE id='{id}';"
            self.cursor.execute(sqlquery)
            log.info(sqlquery)
            return self.cursor.fetchall()
        else:
            return

    def max(self):
        sqllast = f"SELECT MAX(id) FROM t_documento;" 
        self.cursor.execute(sqllast)
        log.info(sqllast)
        max = self.cursor.fetchone()
        return max[0] 

class Archivo(ArchivoDAO):
    def __init__(self):
        try:
            ArchivoDAO.__init__(self)
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))