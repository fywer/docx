import pyodbc,pymysql
import sys
import logging, sys

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)

class SQLServer:
    __instancia = None
    __host = "127.0.0.1"
    __port = 1433
    __database = "docx"
    __user = "sa"
    __password = "ZGF0bw=="
    __server = 'tcp:{0},{1}.database.windows.net'.format(__host, __port)
    log = logging.getLogger('')

    def __new__(cls):
        if cls.__instancia != None:
            return cls.__instancia
        else:
            try:
                cls.__instancia = pyodbc.connect('DRIVER={SQL Server};SERVER='+cls.__server+';DATABASE='+cls.__database+';UID='+cls.__user+';PWD='+cls.__password)
                return cls.__instancia
            except Exception as e:
                cls.log.warn("ERROR: {0}\n".format(e))
                return None

class MySQL:
    _instancia = None
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