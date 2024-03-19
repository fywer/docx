from flask_restful import Resource
import json
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
        
    def get(self, nombre=False):
        if nombre == False:
            try:
                documentos = self.__getDocumentoService().getAllDocumentos()
                return documentos, 200
            except Exception as e:  
                log.warn("ENDPOINT: {0}\n".format(e))
                return {"error": f"Ha ocurrido una exepción. {e}."}, 404
        else:
            try:
                documento = self.__getDocumentoService().getDocumento(nombre)
                return documento,200
            except Exception as e:
                log.warn("ENDPOINT: {0}\n".format(e))
                return {"error": f"Ha ocurrido una exepción. {e}."}, 409

    def post(self):
        try:
            archivo = base64.b64decode(request.json["comprobante"])
            documento = self.__getDocumentoService().setDocumento(archivo)
            return documento,201
        except Exception as e:
            log.warn("ENDPOINT: {0}\n".format(e))
            return eval(f"{e}"), 409

    def put(self):
        try:
            documento = self.__getDocumentoService().updateDocumento(request.json)
            return documento,201
        except Exception as e:
            log.warn("ENDPOINT: {0}\n".format(e))
            return {"error": f"Ha ocurrido una exepción. {e}."}, 409


    def delete(self, nombre):
        try:
            estado = self.__getDocumentoService().deleteDocumento(nombre)
            return estado,205
        except Exception as e:
            log.warn("ENDPOINT: {0}\n".format(e))
            return eval(f"{e}"), 409