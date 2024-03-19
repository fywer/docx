from pymongo import MongoClient
#import pyodbc
#import pymysql
import logging
import sys

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class MongoDB:
    __instancia = None
    __host = "cluster0"
    __user = "ifywerz"
    __password = "5S2ApQdMaod0s6Rl"
    
    def __new__(cls):
        if cls.__instancia is not None:
            return cls.__instancia
        else:
            #mongodb+srv://ifywerz:5S2ApQdMaod0s6Rl@cluster0.n3iivh4.mongodb.net/?retryWrites=true&w=majority
            _url = f'mongodb+srv://{cls.__user}:{cls.__password}@{cls.__host}.n3iivh4.mongodb.net/?retryWrites=true&w=majority'
            try:
                cls.__instancia = MongoClient(_url)
                log.info('Se ha establecido una nueva instancia MongoDB.') 
                return cls.__instancia
            except Exception as e:
                log.warn(f"DRIVER: {e}\n")
                raise Exception("Han ocurrido exepciones de conexión.")
            
class SQLServer:
    __instancia = None
    __host = "192.168.1.200"
    __port = 11433
    __database = "docx"
    __user = "sa"
    __password = "ZGF0bw=="
    # __password = "Company#0"
    __server = f'tcp:{__host},{__port}.database.windows.net'

    def __new__(cls):
        if cls.__instancia is not None:
            return cls.__instancia
        else:
            try:
                cls.__instancia = pyodbc.connect(
                    f'DRIVER=SQL Server;SERVER={cls.__server};DATABASE={cls.__database};UID={cls.__user};PWD={cls.__password}'
                )                
                # cls.__instancia.execute("CREATE DATABASE {0}".format())
                # cls.__instancia.execute("USE DATABASE {0}".format(cls.__database))
                log.info('Se ha establecido una nueva instancia SQLServer.') 
                return cls.__instancia
            except Exception as e:
                log.warn(f"DRIVER: {e}\n")
                raise Exception("Han ocurrido exepciones de conexión.")

class MySQL:
    __instancia = None
    __host = "127.0.0.1"
    __port = 3020
    __database = "docx"
    __user = "ifywerz"
    __password = "Company#256"

    def __new__(cls):
        if cls.__instancia is not None:
            return cls.__instancia
        else:
            try:
                cls.__instancia = pymysql.connect(
                    host=cls.__host,
                    database=cls.__database,
                    user=cls.__user,
                    password=cls.__password,
                    port=cls.__port,
                    max_allowed_packet=16777216,
                    local_infile=True)
                log.info('Se ha establecido una nueva instancia MySQL.') 
                return cls.__instancia
            except Exception as e:
                log.warn(log.warn(f"ERROR: {e}\n"))
                return None