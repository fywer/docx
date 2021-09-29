from ftplib import FTP
from threading import Thread
import sys, logging, time
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class Proceso(Thread):
    __cliente = None

    def __init__(self, cliente):
        Thread.__init__(self)
        self.__cliente = cliente

    def getcliente(self):
        return self.__cliente

    def run(self):
        while True:
            try:
                time.sleep(5)
                bienvenida = self.getcliente().path()
                log.info(bienvenida)
            except Exception as e:
                log.warn(e)
                self.getcliente().exit()
                log.warn("Se ha cerrado la conexión FTP.")
                self.getcliente().connect(host=self.getcliente().gethost, port=self.getcliente().getport)
                self.getcliente().login(user=self.getcliente().getuser, passwd=self.getcliente().getpassword)
                log.warn("Se ha restablecido la conexión FTP.")

class FTPClient(FTP):
    __host = "127.0.0.1"
    __port = 21
    __timeout = None #Segundos
    __user = "fywer"
    __password = "1234"
    
    def __init__(self):
        FTP.__init__(self)
        try:
            bienvenido = self.connect(host=self.__host, port=self.__port, timeout=self.__timeout)
            loggeado = self.login(user=self.__user, passwd=self.__password)
            log.info(loggeado)
            proceso = Proceso(self)
            proceso.start()
        except Exception as e:
            raise Exception("Error en el API FTP.")
    
    @property
    def gethost(self):
        return self.__host
    
    @property
    def getport(self):
        return self.__port

    @property
    def getuser(self):
        return self.__user

    @property
    def getpassword(self):
        return self.__password

    def upload(self, ruta, nombre):
        with open(ruta, 'rb') as archivo:
            self.storbinary('STOR {0}'.format(nombre) , archivo)

    def path(self):
        return self.pwd()

    def download(self):
        pass

    def online(self):
        pass

    def remove(self, ruta):
        self.delete(ruta)

    def exit(self):
        self.close()