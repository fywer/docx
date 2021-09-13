from ftplib import FTP
class FTPClient(FTP):
    __host = "127.0.0.1"
    __port = 21
    __timeout = 864000 #Segundos
    __user = "fywer"
    __password = "1234"
    
    def __init__(self):
        FTP.__init__(self)
        self.connect(host=self.__host, port=self.__port, timeout=self.__timeout)
        self.login(user=self.__user, passwd=self.__password)
        
    def upload(self, ruta, nombre):
        with open(ruta, 'rb') as archivo:
            self.storbinary('STOR {0}'.format(nombre) , archivo)