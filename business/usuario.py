from data.usuario import UsuarioRepository

class UsuarioService:
    def __init__(self):
        self.__dataUsuarioRepository = None
        try:
            self.__dataUsuarioRepository = UsuarioRepository()
        except Exception as e:
            raise Exception(e)

    def __getUsuarioRepository(self):
        return self.__dataUsuarioRepository

    def _existEmail(self, email):
        try:
            if email != None:
                usuario = self.__getUsuarioRepository().findEmailUsuario(email)
                if usuario == None:
                    return {
                        "msg:": "El email no ha sido registrado."
                    }
                else:
                    return usuario
            else:
                raise "El email no ha sido capturado."
        except Exception as e:
            raise Exception("#Business {0}".format(e))

    def _getPassword(self):
        pass

    def suscribirUsuario(self, credencial):
        try:
            usuario = self.__getUsuarioRepository().doInsert(credencial)
            return usuario    
        except Exception as e:
            raise Exception("#Business {0}".format(e))
    
    def autentificarUsuario(self, credencial):
        try:
            self.usuario = self._existEmail(credencial['email'])
            if credencial['password'] == self.usuario['password']:
                # usuario = self.__getUsuarioRepository().doSelect(self.usuario['id'])
                return self.usuario
            else:
                raise Exception("La contraseña no ha sido correcta.")
        except Exception as e:
            raise Exception("#Business {0}".format(e))