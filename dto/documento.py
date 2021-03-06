from flask import request
from flask_restful import Resource
import os, base64, datetime
import queue
from .conexion import MySQL
import logging, sys

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)

class DocumentoDto(Resource):
    url_absoluta = os.path.join(os.getcwd(), "server", "static", "pdf")
    url_relativa = os.path.join("static", "pdf")
    documentos = list()
    log = logging.getLogger('')

    def __init__(self):
        try:
            if not os.path.isdir(self.url_absoluta):
                os.mkdir(self.url_absoluta, 0o777)
            self.db = MySQL()
            self.cursor = self.db.cursor()
        except Exception as e:
            self.log.warn("ERROR: {0}\n".format(e))
            return None
    
    def delete(self, id): 
        for metadoc in self.documentos:
            if id == metadoc["id"]:
                try:
                    sqlquery = f"delete from t_documento where id = {id};"
                    os.remove(os.path.join(self.url_absoluta, metadoc["nombre"]))
                    del(metadoc) #libera
                    self.cursor.execute(sqlquery)
                    self.db.commit()               
                    return {"msg": "El documento ha sido eliminado."}, 201
                except Exception as e:
                    self.log.warn("ERROR: {0}\n".format(e))
                    return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500
        return {"msg" : "El documento no ha sido encontrado."}, 404

    def get(self, id=False):
        if id == False:
            try:
                sqlquery = f"select * from t_documento;"
                self.cursor.execute(sqlquery)
                rows = self.cursor.fetchall() 
                self.documentos.clear()
                documento = {}
                for fila in rows:
                    documento["id"] = fila[0]
                    documento["nombre"] = fila[1]
                    documento["tipo"] = fila[2]
                    documento["tamanio"] = fila[3]
                    documento["ruta"] = fila[4]
                    #documento["fecha"] = str(fila[5])
                    self.documentos.append(documento)
                    documento = {}
                return self.documentos, 200
            except Exception as e:
                self.log.warn("ERROR: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500
        else:
            for metadoc in self.documentos:
                if id == metadoc["id"]:
                    documento = {
                        'id' : metadoc['id'],
                        'nombre' : metadoc['nombre'],
                        'tipo' : metadoc['tipo'],
                        'ruta' : metadoc['ruta'],
                        'tamanio' : metadoc['tamanio']
                        #'fecha' : str(meta['fecha'])
                    }
                    return documento
            return {"msg" : "El documento no ha sido encontrado."}, 404

    def post(self):
        try:
            metadatos = request.json
            pdf = base64.b64decode(metadatos["contenido"])
        except Exception as e:
            self.log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500
        try:
            sqlcount = f"select count(*) from t_documento"
            self.cursor.execute(sqlcount)
            rows = self.cursor.fetchall() 
            documento = {
                "id": rows[0][0] + 1,
                "nombre" : metadatos["nombre"],
                "tipo": metadatos["tipo"],
                "tamanio": metadatos["tamanio"],
                "ruta": os.path.join(self.url_relativa, metadatos["nombre"])
            }
            uri = os.path.join(self.url_absoluta, documento["nombre"])
            if os.path.isfile(uri):
                return {"msg": "El documento ya existe."}, 409
            with open(uri, "wb") as f:
                f.write(pdf)
            documento['ruta'] = documento['ruta'].replace("\\", "/")
            sqlquery = f"insert into t_documento (id, nombre, tipo, ruta, tamanio) " 
            sqlquery += f"values ('{documento['id']}','{documento['nombre']}','{documento['tipo']}','{ documento['ruta']}',{documento['tamanio']});"
            self.cursor.execute(sqlquery)
            self.db.commit()
            self.documentos.append(documento)
            return {"msg" : "El documento ha sido guardado."}, 201
        except Exception as e:
            self.log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500