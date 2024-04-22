from flask_restful import Resource
from flask import request
import base64, logging, sys
from business.comprobante import ComprobanteService

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class ComprobanteEndPoint(Resource):
    def __init__(self):
        self.__comprobanteService = None
        try:
            self.__comprobanteService = ComprobanteService()
        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))

    def __getComprobanteService(self):
        if self.__comprobanteService is not None:
            return self.__comprobanteService
        else:
            raise Exception("El servicio de comprobantes no esta disponible.")
        
    def get(self, nombre=False):
        if nombre == False:
            try:
                documentos = self.__getComprobanteService().getAllComprobantes()
                return documentos, 200
            except Exception as e:  
                log.warn("ENDPOINT: {0}\n".format(e))
                return {"error": f"Ha ocurrido una exepción. {e}."}, 404
        else:
            try:
                documento = self.__getComprobanteService().getComprobante(nombre)
                return documento,200
            except Exception as e:
                log.warn("ENDPOINT: {0}\n".format(e))
                return {"error": f"Ha ocurrido una exepción. {e}."}, 409

    def post(self):
        try:
            archivo = base64.b64decode(request.json["comprobante"])
            documento = self.__getComprobanteService().setComprobante(archivo)
            return documento,201
        except Exception as e:
            log.warn("ENDPOINT: {0}\n".format(e))
            return {"error": f"Ha ocurrido una exepción. {e}."}, 409

    def put(self):
        try:
            documento = self.__getComprobanteService().updComprobante(request.json)
            return documento,201
        except Exception as e:
            log.warn("ENDPOINT: {0}\n".format(e))
            return {"error": f"Ha ocurrido una exepción. {e}."}, 409

    def delete(self, nombre):
        try:
            estado = self.__getComprobanteService().delComprobante(nombre)
            return estado,205
        except Exception as e:
            log.warn("ENDPOINT: {0}\n".format(e))
            return {"error": f"Ha ocurrido una exepción. {e}."}, 409