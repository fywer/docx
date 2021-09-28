from flask import request
from flask_restful import Resource
import time, datetime
import os, base64
import queue
from .conexion import SQLServer, MySQL
from .ftp import FTPClient
import logging, sys
from enum import Enum
from flask_restful import fields, marshal_with

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class ServerDB(Enum):
    SQLSERVER = 1
    MYSQL = 2

class TypeDOC(Enum):
    JPEG = 1
    PNG = 2
    MP4 = 3

class DocumentoDAO:
    def __init__(self):
        self.db = MySQL()
        self.cursor = self.db.cursor()

    def insert(self, id, documento):
        sqlquery = f"insert into t_documento (id, documento) " 
        sqlquery += f"values ('{id}','{documento}');"
        self.cursor.execute(sqlquery)
        self.db.commit()
    
    def delete(self, id):
        sqlquery = f"delete from t_documento where id = {id};"
        self.cursor.execute(sqlquery)
        self.db.commit()

    def select(self, id=False):
        if id != False:
            sqlquery = f"select * from t_documento where id='{id}';"
            self.cursor.execute(sqlquery)
            return self.cursor.fetchall()
        else:
            return

class MetadatoDAO:
    def __init__(self):
        self.db = SQLServer()
        self.cursor = self.db.cursor()

    def count(self):
        sqlcount = f"select count(*) from t_documento"
        self.cursor.execute(sqlcount)
        return self.cursor.fetchall()

    def insert(self, documento):
        sqlquery = f"insert into t_documento (id, nombre, tipo, ruta, tamanio) " 
        sqlquery += f"values ('{documento['id']}','{documento['nombre']}','{documento['tipo']}','{ documento['ruta']}',{documento['tamanio']});"
        self.cursor.execute(sqlquery)
        self.db.commit()

    def delete(self, id):
        sqlquery = f"delete from t_documento where id = {id};"
        self.cursor.execute(sqlquery)
        self.db.commit()

    def select(self, id=False):
        if id == False:
            sqlquery = f"select * from t_documento order by fecha desc;"
            self.cursor.execute(sqlquery)
            rows = self.cursor.fetchall()
            return rows
        else:
            pass

class Metadato(MetadatoDAO):
    def __init__(self):
        MetadatoDAO.__init__(self)

    def findByType(self, tipo):
        sqlquery = f"select * from t_documento where tipo='{tipo}';"
        self.cursor.execute(sqlquery)
        rows = self.cursor.fetchall()
        return rows

class DocumentoBO(Resource):
    url_absoluta = os.path.join("c:\\", "Users", "fywer", "Google Drive")
    #os.chdir(url_absoluta)
    #url_relativa = os.path.join("ftp:\\", "fywer:1234@", "127.0.0.1")
    
    documentos = list()
    metadatodao = Metadato()
    documentodao = DocumentoDAO()    
    clientftp = FTPClient()

    #clientftp.gethost = "192.168.1.137"
    url_relativa = f"ftp:\\{clientftp.getuser}:{clientftp.getpassword}@{clientftp.gethost}"

    def __init__(self):
        try:
            if not os.path.isdir(self.url_absoluta):
                os.mkdir(self.url_absoluta, 0o777)
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
            return None
    
    @classmethod
    def getdocumentodao(cls, index):
        #SQLServer
        if index is ServerDB.SQLSERVER:
            return cls.metadatodao
        #MySQL
        elif index is ServerDB.MYSQL:
            return cls.documentodao
    
    @classmethod
    def getTipoDocumento(cls, tipo):
        if tipo == 'png':
            return TypeDOC.PNG
        if tipo == 'jpeg':
            return TypeDOC.JPEG
        if tipo == 'mp4':
            return TypeDOC.MP4

    @classmethod
    def getclientftp(cls):
        return cls.clientftp

    def setNombre(self, tipo):
        ahora = datetime.datetime.now()
        fecha = ahora.strftime("%Y%m%d-%H%M%S-%f")
        if tipo == TypeDOC.JPEG:
            return f'IMG-{fecha}.jpg'
        if tipo == TypeDOC.PNG:
            return f'IMG-{fecha}.png'
        if tipo == TypeDOC.MP4:
            return f'VID-{fecha}.mp4'

    def delete (self, id): 
        for metadoc in self.documentos:
            if id == metadoc["id"]:
                try:
                    try:
                        self.getdocumentodao(ServerDB.SQLSERVER).delete(id) 
                        log.info("LOS METADATOS HAN SIDO ELIMINADOS EN SQLSERVER.")
                        self.getdocumentodao(ServerDB.MYSQL).delete(id)
                        log.info("EL ARCHIVO HA SIDO ELIMINADO EN MYSQL.")
                        #Por definir eliminar en FTP
                        self.getclientftp().remove(metadoc["nombre"])
                        log.info("EL ARCHIVO HA SIDO ELIMINADO EN FTP.")
                        try:
                            os.remove(os.path.join(self.url_absoluta, metadoc["nombre"]))
                            log.info("EL ARCHIVO HA SIDO ELIMINADO EN CLOUD.")
                            del(metadoc) #libera memoria
                            log.info("LOS METADATOS HAN SIDO ELIMINADOS EN MEMORIA.")
                        except Exception as e:
                            log.warn("ERROR CLOUD: {0}\n".format(e))
                            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500    
                        return {"msg": "El documento ha sido eliminado."}, 201
                    except Exception as e:
                        log.warn("ERROR DB: {0}\n".format(e))
                        return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500

                except Exception as e:
                    log.warn("ERROR: {0}\n".format(e))
                    return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
        
        return {"msg" : "El documento no ha sido encontrado."}, 404

    def get(self, id=False):
        if id == False:
            try:
                rows = self.getdocumentodao(ServerDB.SQLSERVER).select() 
                self.documentos.clear()
                documento = {}
                for fila in rows:
                    documento["id"] = fila[0]
                    documento["nombre"] = fila[1]
                    documento["tipo"] = fila[2]
                    documento["ruta"] = fila[3]
                    documento["tamanio"] = fila[4]
                    self.documentos.append(documento)
                    documento = {}
                return self.documentos, 200
            except Exception as e:
                log.warn("ERROR: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
        else:
            for metadoc in self.documentos:
                if id == metadoc["id"]:
                    contenido = self.getdocumentodao(ServerDB.MYSQL).select(id)
                    documento = {
                        'id' : metadoc['id'],
                        'nombre' : metadoc['nombre'],
                        'tipo' : metadoc['tipo'],
                        'ruta' : metadoc['ruta'],
                        'tamanio' : metadoc['tamanio'],
                        'contenido' : contenido[0][1]
                    }
                    return documento
            return {"msg" : "El documento no ha sido encontrado."}, 404

    def post(self):
        try:
            metadatos = request.json
            archivo = base64.b64decode(metadatos["contenido"])
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
        try:
            tipo = metadatos["tipo"].split('/')[1]
            if tipo != 'png' and tipo != 'jpeg' and tipo != 'mp4' :
                return {"msg" : "El formato no ha sido aceptado."}, 406 
            nombre = self.setNombre(self.getTipoDocumento(tipo))
            documento = {
                "id": self.getdocumentodao(ServerDB.SQLSERVER).count()[0][0] + 1,
                "nombre" : nombre,
                "tipo": tipo,
                "tamanio": metadatos["tamanio"],
                "ruta": os.path.join(self.url_relativa, nombre)
            }
            try:
                uri_cloud = os.path.join(self.url_absoluta, documento["nombre"])
                if os.path.isfile(uri_cloud):
                    return {"msg": "El documento ya existe."}, 409
                #documento['ruta'] = documento['ruta'].replace("\\", "/")
                self.documentos.append(documento)
                log.info("LOS METADATOS HAN SIDO ALMACENADOS EN MEMORIA.")
                with open(uri_cloud, "wb") as f:
                    f.write(archivo)
                log.info("EL ARCHIVO HA SIDO ALMACENADO EN CLOUD.")
            except:
                log.warn("ERROR CLOUD: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500    
            try:
                self.getclientftp().upload(uri_cloud, documento["nombre"])
                log.info("EL ARCHIVO HA SIDO ALMACENADO EN FTP.")
                try:
                    self.getdocumentodao(ServerDB.MYSQL).insert(documento["id"], metadatos["contenido"])
                    log.info("EL ARCHIVO HA SIDO ALMACENADO EN MYSQL.")
                    self.getdocumentodao(ServerDB.SQLSERVER).insert(documento)
                    log.info("LOS METADATOS HAN SIDO ALMACENADOS EN SQLSERVER.")
                except Exception as e:
                    log.warn("ERROR BD: {0}\n".format(e))
                    return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
            except Exception as e:
                log.warn("ERROR FTP: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
            return {"msg" : "El documento ha sido guardado."}, 200
        
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500

class DocumentoTipoBO(Resource):
    documentos = list()
    metadatodao = Metadato()
    documentodao = DocumentoDAO()
    def __init__(self):
        pass
    @classmethod
    def getdocumentodao(cls, index):
        #SQLServer
        if index is ServerDB.SQLSERVER:
            return cls.metadatodao
        #MySQL
        elif index is ServerDB.MYSQL:
            return cls.documentodao

    def post(self):
        tipos = request.json
        documentosByType = []
        try:
            for tipo in tipos:
                rows = self.getdocumentodao(ServerDB.SQLSERVER).findByType(tipo)
                for fila in rows:
                    documento = {}
                    documento["id"] = fila[0]
                    documento["nombre"] = fila[1]
                    documento["tipo"] = fila[2]
                    documento["ruta"] = fila[3]
                    documento["tamanio"] = fila[4]
                    documentosByType.append(documento)
            return documentosByType, 200
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500

