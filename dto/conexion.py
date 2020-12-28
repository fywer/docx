import pymysql
import sys
import logging, sys
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
class MySQL:
    _instancia = None #conexion
    _host = "127.0.0.1"
    _database = "docx"
    _user = "ifywerz"
    _password = "company"
    log = logging.getLogger('')

    def __new__(cls):
        if cls._instancia != None:
            return cls._instancia
        else:
            try:
                cls._instancia = pymysql.connect(host=cls._host, database=cls._database, user=cls._user, password=cls._password)
                return cls._instancia
            except Exception as e:
                cls.log.warn("ERROR: {0}\n".format(e))
                return None