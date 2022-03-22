from flask import request
from flask_restful import Resource
import logging, sys, hashlib, base64, datetime, os
from enum import Enum
from dao.archivo import  Archivo
from dao.metadato import Metadato

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

class DocumentoBO(Resource):
    documentos = list()
    metadatodao = Metadato()
    archivodao = Archivo()    
    basepath = os.path.join(os.getcwd(), "server", "static", "img")
    relativa = os.path.join("static", "img")

    @classmethod
    def getarchivodao(cls, index):
        #SQLServer
        if index is ServerDB.SQLSERVER:
            return cls.metadatodao
        #MySQL
        elif index is ServerDB.MYSQL:
            return cls.archivodao

    @classmethod
    def getdocumentos(cls):
        return cls.documentos
    
    @classmethod
    def getdocumento(cls, id):
        id = int(id)
        for metadoc in cls.documentos:
            if id == metadoc["id"]:
                contenido = cls.getarchivodao(ServerDB.MYSQL).select(id)
                documento = {
                    'id' : metadoc['id'],
                    'nombre' : metadoc['nombre'],
                    'tipo' : metadoc['tipo'],
                    'ruta' : metadoc['ruta'],
                    'tamanio' : metadoc['tamanio'],
                    'contenido' : contenido[0][1]
                }
                return documento

    def delete (self, id): 
        for metadoc in self.documentos:
            if id == metadoc["id"]:
                try:
                    try:
                        os.remove(os.path.join(self.basepath, metadoc["nombre"]))
                        log.info("El documento han sido eliminados en Google Drive.")

                        self.getarchivodao(ServerDB.SQLSERVER).delete(id) 
                        log.info("Los metadatos han sido eliminados en sqlserver.")
                        
                        self.getarchivodao(ServerDB.MYSQL).delete(id)
                        log.info("El archivo ha sido eliminado en mysql.")
                    except Exception as e:
                        log.warn("ERROR DB: {0}\n".format(e))
                        return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
                    
                    del(metadoc) #libera memoria
                    log.info("Los metadatos han sido eliminados en memoria.")
                    return {"msg": "El documento ha sido eliminado."}, 201
                
                except Exception as e:
                    log.warn("ERROR: {0}\n".format(e))
                    return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500

        return {"msg" : "El documento no ha sido encontrado."}, 404

    def get(self, id=False):
        if id == False:
            try:
                rows = self.getarchivodao(ServerDB.SQLSERVER).select() 
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
                log.warn(self.documentos)
                if id == metadoc["id"]:
                    contenido = self.getarchivodao(ServerDB.MYSQL).select(id)
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
            tipo = metadatos["tipo"]
            if tipo != 1 and tipo != 2 and tipo != 3 :
                return {"msg" : "El formato no ha sido aceptado."}, 406 
            try:
                self.getarchivodao(ServerDB.MYSQL).insert(metadatos["contenido"])
                log.info("El archivo ha sido almacenado en MySQL.")
                
                
                documento = {
                    "id": self.getarchivodao(ServerDB.MYSQL).max(),
                    "nombre" : hashlib.new(name="sha256",  data=archivo).hexdigest(),
                    "tipo": tipo,
                    "tamanio": metadatos["tamanio"]
                }
                uri_cloud = os.path.join(self.basepath, documento["nombre"])
                documento["ruta"] = os.path.join(self.relativa, documento["nombre"])
                
                if os.path.isfile(uri_cloud):
                    return {"msg", "El documento ya existe."}, 409 
                with open(uri_cloud, "wb") as f:
                    f.write(archivo) 
                log.info("El archivo ha sido almacenado en Google Drive.")
                
                self.documentos.append(documento)
                log.info("Los metadatos han sido almacenados en memoria.") 
                log.info(documento)

                self.getarchivodao(ServerDB.SQLSERVER).insert(documento)
                log.info("Los metadatos han sido almacenados en SQLServer..")

            except Exception as e:
                log.warn("ERROR BD: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500

            return {"msg" : "El documento ha sido guardado."}, 200
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500

class DocumentoTipoORDateBO(Resource):
    documentos = list()
    metadatodao = Metadato()
    archivodao = Archivo()
    def __init__(self):
        pass
    @classmethod
    def getarchivodao(cls, index):
        #SQLServer
        if index is ServerDB.SQLSERVER:
            return cls.metadatodao
        #MySQL
        elif index is ServerDB.MYSQL:
            return cls.archivodao

    def post(self):
        parametros = request.json
        self.documentos.clear()
        log.warn(parametros)
        if type(parametros) is list:
            try:
                for tipo in parametros:
                    rows = self.getarchivodao(ServerDB.SQLSERVER).findByType(tipo)
                    for fila in rows:
                        documento = {}
                        documento["id"] = fila[0]
                        documento["nombre"] = fila[1]
                        documento["tipo"] = fila[2]
                        documento["ruta"] = fila[3]
                        documento["tamanio"] = fila[4]
                        #documentosByType.append(documento)
                        self.documentos.append(documento)
                return self.documentos, 200
            except Exception as e:
                log.warn("ERROR: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
        elif type(parametros) is dict:
            try:
                inicio = parametros['inicio']
                final = parametros['final']
                rows = self.getarchivodao(ServerDB.SQLSERVER).findByDate(inicio, final)
                for fila in rows:
                        documento = {}
                        documento["id"] = fila[0]
                        documento["nombre"] = fila[1]
                        documento["tipo"] = fila[2]
                        documento["ruta"] = fila[3]
                        documento["tamanio"] = fila[4]
                        #documentosByType.append(documento)
                        self.documentos.append(documento)
                return self.documentos, 200
            except Exception as e:
                log.warn("ERROR: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500