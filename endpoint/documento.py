
from flask_restful import Resource
from flask import request, jsonify
import logging, sys, base64
from business.documento import DocumentoService

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
from enum import Enum

class TYPE(Enum):
    XML = 1


class DocumentoEndPoint(Resource):
    def __init__(self):
        self.__documentoService = None
        try:
            self.__documentoService = DocumentoService()
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))

    def __getDocumentoService(self):
        if self.__documentoService is not None:
            return self.__documentoService
        else:
            raise Exception("El servicio de documentación no esta disponible.")
        
    def get(self, id=False):
        if id == False:
            try:
                documentos = self.__getDocumentoService().getAllDocumentos()
                return documentos, 200
            except Exception as e:  
                log.warn("ENDPOINT: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 404
        else:
            try:
                documento = self.__getDocumentoService().getDocumento(id)
                return documento, 200
            except Exception as e:
                log.warn("ENDPOINT: {0}\n".format(e))
                return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 404

    def post(self):
        try:
            archivo = base64.b64decode(request.json["comprobante"])
            documento = self.__getDocumentoService().setDocumento(archivo)
            return documento.dict(),201
        except Exception as e:
            log.warn("ENDPOINT: {0}\n".format(e))
            return {"error": f"Ha ocurrido una exepción. {e}."}, 409

    def delete(self, id):
        try:
            estado = self.__getDocumentoService().deleteDocumento(id)
            return estado, 200
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 404

# class DocumentoTipoDateEndPoint(Resource):
#     documentos = list()
#     metadatodao = Metadato()
#     archivodao = Archivo()
#     def __init__(self):
#         pass
#     @classmethod
#     def getarchivodao(cls, index):
#         #SQLServer
#         if index is ServerDB.SQLSERVER:
#             return cls.metadatodao
#         #MySQL
#         elif index is ServerDB.MYSQL:
#             return cls.archivodao

#     def post(self):
#         parametros = request.json
#         self.documentos.clear()
#         log.warn(parametros)
#         if type(parametros) is list:
#             try:
#                 for tipo in parametros:
#                     rows = self.getarchivodao(ServerDB.SQLSERVER).findByType(tipo)
#                     for fila in rows:
#                         documento = {}
#                         documento["id"] = fila[0]
#                         documento["nombre"] = fila[1]
#                         documento["tipo"] = fila[2]
#                         documento["ruta"] = fila[3]
#                         documento["tamanio"] = fila[4]
#                         #documentosByType.append(documento)
#                         self.documentos.append(documento)
#                 return self.documentos, 200
#             except Exception as e:
#                 log.warn("ERROR: {0}\n".format(e))
#                 return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500
#         elif type(parametros) is dict:
#             try:
#                 inicio = parametros['inicio']
#                 final = parametros['final']
#                 rows = self.getarchivodao(ServerDB.SQLSERVER).findByDate(inicio, final)
#                 for fila in rows:
#                         documento = {}
#                         documento["id"] = fila[0]
#                         documento["nombre"] = fila[1]
#                         documento["tipo"] = fila[2]
#                         documento["ruta"] = fila[3]
#                         documento["tamanio"] = fila[4]
#                         #documentosByType.append(documento)
#                         self.documentos.append(documento)
#                 return self.documentos, 200
#             except Exception as e:
#                 log.warn("ERROR: {0}\n".format(e))
#                 return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 500