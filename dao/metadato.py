from .conexion import SQLServer
import logging, sys
from datetime import date

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class MetadatoDAO:
    def __init__(self):
        self.db = SQLServer()
        try:
            self.cursor = self.db.cursor()
        except Exception as e:
            raise Exception(e) 
    
    def count(self):
        sqlcount = f"SELECT COUNT(*) FROM t_documento"
        self.cursor.execute(sqlcount)
        log.info(sqlcount)
        return self.cursor.fetchall()

    def insert(self, documento):
        sqlquery = f"INSERT INTO t_documento (id, nombre, tipo, ruta, tamanio) " 
        sqlquery += f"VALUES ('{documento['id']}','{documento['nombre']}','{documento['tipo']}','{ documento['ruta']}',{documento['tamanio']});"
        self.cursor.execute(sqlquery)
        self.db.commit()
        log.info(sqlquery)

    def delete(self, id):
        sqlquery = f"DELETE FROM t_documento WHERE id = {id};"
        self.cursor.execute(sqlquery)
        self.db.commit()
        log.info(sqlquery)

    def select(self, id=False):
        if id == False:
            sqlquery = f"SELECT * FROM t_documento ORDER BY fecha DESC;"
            self.cursor.execute(sqlquery)
            rows = self.cursor.fetchall()
            log.info(sqlquery)
            return rows
        else:
            pass

class Metadato(MetadatoDAO):
    def __init__(self):
        try:
            MetadatoDAO.__init__(self)
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
    
    def findByType(self, tipo):
        sqlquery = f"SELECT * FROM t_documento WHERE tipo='{tipo}';"
        self.cursor.execute(sqlquery)
        rows = self.cursor.fetchall()
        log.info(sqlquery)
        return rows

    def findByDate(self, inicio, final):
        i = date.fromisoformat(inicio)
        f = date.fromisoformat(final)
        diainicio, mesinicio, anioinicio = i.day, i.month, i.year
        diafinal, mesfinal, aniofinal = f.day, f.month, f.year
        sqlquery = f'''SELECT * FROM t_documento WHERE 
        ( YEAR(fecha) >= {anioinicio} AND YEAR(fecha) <= {aniofinal} ) 
        AND ( MONTH(fecha) >= {mesinicio} AND MONTH(fecha) <= {mesfinal} ) 
        AND ( DAY(fecha) >= {diainicio} AND DAY(fecha) <= {diafinal} )'''
        self.cursor.execute(sqlquery)
        rows = self.cursor.fetchall()
        log.info(sqlquery)
        return rows
