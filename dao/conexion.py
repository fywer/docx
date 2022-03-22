import pyodbc,pymysql
import sys
import logging, sys

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class SQLServer:
    __instancia = None
    __host = "127.0.0.1"
    __port = 2919
    __database = "docx"
    __user = "sa"
    __password = "ZGF0bw==2331i"
    __server = 'tcp:{0},{1}.database.windows.net'.format(__host, __port)

    def __new__(cls):
        if cls.__instancia != None:
            return cls.__instancia
        else:
            try:
                cls.__instancia = pyodbc.connect('DRIVER={SQL Server};SERVER='+cls.__server+';DATABASE='+cls.__database+';UID='+cls.__user+';PWD='+cls.__password)
                log.info('Se ha establecido una nueva instacia SQLServer.') 
                return cls.__instancia
            except Exception as e:
                log.warn("ERROR: {0}\n".format(e))
                return None

class MySQL:
    __instancia = None
    __host = "127.0.0.1"
    __port = 3020
    __database = "docx"
    __user = "ifywerz"
    __password = "company256"

    def __new__(cls):
        if cls.__instancia != None:
            return cls.__instancia
        else:
            try:
                cls.__instancia = pymysql.connect(host=cls.__host, database=cls.__database, user=cls.__user, password=cls.__password, port=cls.__port, max_allowed_packet=16777216,  local_infile=True)
                log.info('Se ha establecido una nueva instacia MySQL.') 
                return cls.__instancia
            except Exception as e:
                log.warn("ERROR: {0}\n".format(e))
                return None