from flask import request
from flask_restful import Resource
import time
import os, base64
import queue
from .conexion import SQLServer
import logging, sys

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
class DocumentoDAO:
    def __init__(self):
        #self.db = MySQL()
        self.db = SQLServer()
        self.cursor = self.db.cursor()

    def insert(self, documento):
        #sqlcount = f"select count(*) from t_documento"
        #self.cursor.execute(sqlcount)
        #rows = self.cursor.fetchall()
        
            #sqlquery = f"insert into t_documento (id, nombre, tipo, ruta, tamanio) " 
            #sqlquery += f"values ('{documento['id']}','{documento['nombre']}','{documento['tipo']}','{ documento['ruta']}',{documento['tamanio']});"
            
        sqlquery = f"insert into t_documento (nombre, tipo, ruta, tamanio) " 
        sqlquery += f"values ('{documento['nombre']}','{documento['tipo']}','{ documento['ruta']}',{documento['tamanio']});"
        self.cursor.execute(sqlquery)
        self.db.commit()

    def delete(self, id):
        sqlquery = f"delete from t_documento where id = {id};"
        self.cursor.execute(sqlquery)
        self.db.commit()

    def select(self, id=False):
        if id == False:
            sqlquery = f"select * from t_documento;"
            self.cursor.execute(sqlquery)
            rows = self.cursor.fetchall()
            return rows
        else:
            pass        

class DocumentoBO(Resource):
    url_absoluta = os.path.join(os.getcwd(), "server", "static", "pdf")
    url_relativa = os.path.join("static", "pdf")
    documentos = list()
    documentodao = DocumentoDAO()
    log = logging.getLogger('')

    def __init__(self):
        try:
            if not os.path.isdir(self.url_absoluta):
                os.mkdir(self.url_absoluta, 0o777)

        except Exception as e:
            self.log.warn("ERROR: {0}\n".format(e))
            return None
    
    @classmethod
    def getdocumentodao(cls):
        return cls.documentodao

    def setNombre(self, tipo):
        ahora = time.localtime()
        fecha = "{0}{1}{2}-{3}{4}{5}".format(ahora.tm_year, ahora.tm_mon, ahora.tm_mday, ahora.tm_hour, ahora.tm_min, ahora.tm_sec)
        if tipo == 'jpeg':
            return 'IMG-{}.jpg'.format(fecha)
        if tipo == 'png':
            return 'IMG-{}.png'.format(fecha)
        if tipo == 'mp4' :
            return 'VID-{}.mp4'.format(fecha)

    def delete (self, id): 
        for metadoc in self.documentos:
            if id == metadoc["id"]:
                try:
                    try:
                        self.getdocumentodao().delete(id) 
                        os.remove(os.path.join(self.url_absoluta, metadoc["nombre"]))
                        del(metadoc) #libera
                        return {"msg": "El documento ha sido eliminado."}, 201
                    except Exception as e:
                        self.log.warn("ERROR DB: {0}\n".format(e))
                        return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500

                except Exception as e:
                    self.log.warn("ERROR: {0}\n".format(e))
                    return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500
        
        return {"msg" : "El documento no ha sido encontrado."}, 404

    def get(self, id=False):
        if id == False:
            try:
                rows = self.getdocumentodao().select() 
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
            tipo = metadatos["tipo"].split('/')[1]
            if tipo != 'png' and tipo != 'jpeg' and tipo != 'mp4' :
                return {"msg" : "El formato no ha sido aceptado."}, 406 
            documento = {
                #"id": rows[0][0] + 1,
                "nombre" : self.setNombre(tipo),
                "tipo": tipo,
                "tamanio": metadatos["tamanio"],
                "ruta": os.path.join(self.url_relativa, self.setNombre(tipo))
            }
            uri = os.path.join(self.url_absoluta, documento["nombre"])
            if os.path.isfile(uri):
                return {"msg": "El documento ya existe."}, 409
            documento['ruta'] = documento['ruta'].replace("\\", "/")
            try:   
                self.getdocumentodao().insert(documento)
                self.documentos.append(documento)
                with open(uri, "wb") as f:
                    f.write(pdf) #Por definir
                return {"msg" : "El documento ha sido guardado."}, 201
            except Exception as e:
                self.log.warn("ERROR BD: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500
        except Exception as e:
            self.log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico"}, 500