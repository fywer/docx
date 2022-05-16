from importlib.metadata import metadata
from flask_restful import Resource
from flask import request
import logging, sys
from business.usuario import UsuarioService 

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class UsuarioEndPoint(Resource):
    def __init__(self):
        self.__usuarioService = None
        try:
            self.__usuarioService = UsuarioService()

        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
    
    def __getUsuarioService(self):
        return self.__usuarioService

    def post(self):
        try:
            metadatos = request.json
            credencial = metadatos
            usuario = self.__getUsuarioService().suscribirUsuario(credencial)
            response = {
                "msg" : {
                    'usuario': usuario
                },
                "error" : {
                    "codigo" : 0
                }
            }
            return response, 200

        except Exception as e:
            log.warn("ERROR: {0}\n".format(e))
            return {
                "msg": "Ha ocurrido una exepción. Contacta soporte técnico.",
                "err": "{0}".format(e)
            }, 404
            return {"msg": "Ha ocurrido una exepción. Contacta soporte técnico."}, 404