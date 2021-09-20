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

    def run(self):
        while True:
            try:
                time.sleep(2)
                bienvenida = self.__cliente.path()
                log.info(bienvenida)
            except Exception as e:
                log.warn(e)

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

    def upload(self, ruta, nombre):
        with open(ruta, 'rb') as archivo:
            self.storbinary('STOR {0}'.format(nombre) , archivo)

    def path(self):
        return self.pwd()

    def download(self):
        pass