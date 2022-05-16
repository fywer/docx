# from interface.usuario import IUsuarioData
from abc import ABC, abstractmethod
from util.conexion import SQLServer
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s %(message)s',
    stream=sys.stderr
)
log = logging.getLogger('')
class IUsuarioData(ABC):
    @abstractmethod
    def doInsert(self, usuario):
        pass

    @abstractmethod
    def doDelete(self, id):
        pass

    @abstractmethod
    def doSelect(self, id=False):
        pass


class UsuarioRepository(IUsuarioData):

    def __init__(self):
        self.__db = SQLServer()
        try:
            self.__cursor = self.__db.cursor()
        except Exception as e:
            raise Exception(e)

    def __getEntity(self):
        return self.__cursor

    def findEmailUsuario(self, email):
        try:
            sqlquery = f"SELECT * FROM t_usuario WHERE email='{email}'"
            log.info(sqlquery)
            self.__getEntity().execute(sqlquery)
            data = self.__getEntity().fetchone()
            if data != None:
                return {
                    'id': data[0],
                    'email': data[1],
                    'password': data[2]
                }
            else:
                raise Exception("El correo no ha sido registrado.")
        except Exception as e:
            raise Exception("#Data {0}".format(e))

    def doInsert(self, usuario):
        sqlquery = f"INSERT INTO t_usuario (email, password) "
        sqlquery += f"VALUES ('{usuario['email']}', '{usuario['password']}');"
        try:
            self.__getEntity().execute(sqlquery)
            self.__getEntity().commit()
        except Exception as e:
            raise Exception("#Data {0}".format(e))

    def doDelete(self, id):
        sqlquery = f"DELETE FROM t_usuario WHERE id = {id};"
        try:
            log.info(sqlquery)
            self.__getEntity().execute(sqlquery)
            self.__getEntity().commit()
        except Exception as e:
            raise Exception(e)

    def doSelect(self, id=False):
        if id == False:
            sqlquery = f"SELECT * FROM t_usuario ORDER BY fecha DESC;"
            try:
                log.info(sqlquery)
                self.__getEntity().execute(sqlquery)
                rows = self.__getEntity().fetchall()
                usuarios = list()
                for data in rows:
                    usuario = {
                        'id': data[0],
                        'correo': data[1],
                        'password': data[2]
                    }
                usuarios.append(usuario)
                return usuario
            except Exception as e:
                raise Exception("#Data {0}".format(e))
        else:
            try:
                sqlquery = f"SELECT * FROM t_usuario WHERE id='{int(id)}'"
                self.__getEntity().execute(sqlquery)
                data = self.__getEntity().fetchone()

                if data != None:
                    return {
                        'id': data[0],
                        'correo': data[1],
                        'password': data[2]
                    }
                else:
                    return False
            except Exception as e:
                raise Exception("#Data {0}".format(e))
