import re, base64
from datetime import datetime
from lxml import etree
from OpenSSL import crypto
from Crypto.Hash import SHA256
from Crypto.Signature  import PKCS1_v1_5
from Crypto.PublicKey import RSA

import logging
import sys
import signxml

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class CertificadoService:
    # __xlstpath = 'http://www.sat.gob.mx/sitio_internet/cfd/3/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt'
    # __xlstpath = os.path.join("E:", "Data", "xslt", "sat.gob.mx_sitio_internet_cfd_4_cadenaoriginal_4_0.xslt")
    BEGIN_CERTIFICATE = '-----BEGIN CERTIFICATE-----\n'
    END_CERTIFICATE = '\n-----END CERTIFICATE-----\n'
    DEBUG = False
    __xsdpath = r'./server/config/xsd/cfdv40.xsd'
    #__xsdpath = r'./server/config/xsd/ComercioExterior20.xsd'
    __xlstpath = r'./server/config/xlst/cadenaoriginal_4_0.xslt'

    def __init__(self, certificado, llave, Debug=None):
        self.__pathCertificado = certificado
        self.__pathKey = self.__getCertificadox509PrivateKey(llave)
        self.__pathCer = self.__getCertificadox509PublicKey(certificado)
        if Debug is not None:
            self.DEBUG = Debug
    
    @property
    def _getPathXSD(self):
        return self.__xsdpath
    
    @property
    def _getPathXLST(self):
        return self.__xlstpath

    @property
    def _getPathKey(self):
        return self.__pathKey
    
    @property
    def _getPathCer(self):
        return self.__pathCer
    
    @property
    def _getPathCertificado(self):
        return self.__pathCertificado
    
    def getRfcEmisor(self):
        return self.rfcEmisor
    
    def getRfcReceptor(self):
        return self.rfcReceptor
    
    def getTipoComprobante(self):
        return self.tipoDeComprobante
    
    def __getCertificadox509PublicKey(self, certpath):
        key = RSA.import_key(open(certpath, "rb").read())
        pu_key_string = key.exportKey()
        with open ("./server/config/PUB_EKU9003173C9.pem", "w") as pub_file:
            print("{}".format(pu_key_string.decode()), file=pub_file)
        return "./server/config/PUB_EKU9003173C9.pem"

    def __getCertificadox509PrivateKey(self, llavepath, passw="12345678a"):
        key = RSA.import_key(open(llavepath, "rb").read(), passphrase=passw)
        pv_key_string = key.exportKey()
        with open ("./server/config/PRI_EKU9003173C9.pem", "w") as prv_file:
            print("{}".format(pv_key_string.decode()), file=prv_file)
        return "./server/config/PRI_EKU9003173C9.pem"

    def _getCertificadoData(self, rutaCertificado):    
        with open(rutaCertificado, 'rb') as f:
            __dataCert = f.read()
        return __dataCert
    
    def _getLlaveData(self, rutaLlave):    
        with open (rutaLlave, 'rb') as f:
            __privateKey = f.read()
        return __privateKey
    
    def isCancelacion(self, xmlFile, xsdFile):
        pass

    def isComprobante(self, xmlFile, xsdFile):
        try:
            cfdi = etree.parse(xmlFile) 
            schema = etree.XMLSchema(file=xsdFile) 
            schema.assertValid(cfdi)
        except Exception as e:
            log.warn(f"CERT: {e}\n")
            raise Exception( "El documento no es un comprobante fiscal." )

    def cancelar(self, xmlPath):
        # Define un diccionario de espacios de nombres.
        namespaces = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }
        try:
            # Intenta leer un archivo XML ubicado en xmlPath y obtiene su raíz.
            cancelacion = etree.parse(xmlPath).getroot()
            # Agrega un atributo "Fecha" al elemento raíz con la fecha y hora actuales.
            cancelacion.attrib['Fecha'] = str(datetime.now().isoformat())[:19]
            # Firma el documento XML usando un algoritmo de firma RSA-SHA1 con el algoritmo de hash SHA1 y una forma canónica de C14N (canonización).
            signer = signxml.XMLSigner(signature_algorithm="rsa-sha1",digest_algorithm="sha1",c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
            signer.namespaces = {None: signxml.namespaces.ds}
            signer_xml = signer.sign(cancelacion, key=self._getLlaveData(self._getPathKey), cert=self._getCertificadoData(self._getPathCer))
            # Obtiene ciertos elementos del documento firmado.
            folios, signature = signer_xml.getchildren()
            signedInfo, signatureValue, keyInfo = signature.getchildren()
            x509Data = keyInfo.getchildren()
            # Obtiene el certificado en formato base64.
            cert64 = self.__getCertificado64()
            certificado = self.__getCertificadox509(cert64)

            # Añade elementos adicionales al nodo de información de clave (KeyInfo) del certificado.
            x509IssuerSerial = etree.SubElement(x509Data[0],'X509IssuerSerial')
            x509IssuerName = etree.SubElement(x509IssuerSerial,'X509IssuerName')
            x509IssuerName.text = '''OID.1.2.840.113549.1.9.2=responsable: ACDMA-SAT, OID.2.5.4.45=2.5.4.45, L=COYOACAN, S=CIUDAD DE MEXICO, C=MX, PostalCode=06370, STREET=3ra cerrada de caliz, E=oscar.martinez@sat.gob.mx, OU=SAT-IES Authority, O=SERVICIO DE ADMINISTRACION TRIBUTARIA, CN=AC UAT'''
            x509SerialNumber = etree.SubElement(x509IssuerSerial,'X509SerialNumber')
            x509SerialNumber.text = str(certificado.get_serial_number())
            X509Certificate = etree.SubElement(x509Data[0], 'X509Certificate')
            X509Certificate.text = cert64
            tree = etree.ElementTree(signer_xml)
            # Convierte el árbol de XML firmado en una cadena de bytes codificada en UTF-8.
            xmlCancelacionData = etree.tostring(tree, encoding="utf-8")
            log.info(f"CERT: {'El sistema ha generado xml firmado.'}\n")
            return xmlCancelacionData 

        except Exception as e:
            # Si se produce alguna excepción durante este proceso, se registra un mensaje de advertencia en el registro y se eleva una excepción con un mensaje indicando que la cancelación del comprobante no se ha realizado.
            log.warn(f"CERT: {e}\n")
            raise Exception("El comprobante no ha sido cancelado.")


    def sellar(self, xmlPath):
        try:
            # self.isComprobante(xmlPath, self._getPathXSD)
            # Obtiene la fecha y hora actual en formato ISO y la convierte en una cadena de longitud 19.
            fecha = str(datetime.now().isoformat())[:19]
            # Intenta leer el archivo XML ubicado en xmlPath y Obtiene la raíz del árbol XML.
            arbol = etree.parse(xmlPath).getroot()
            # Obtiene el certificado en formato base64 y su correspondiente objeto certificado.
            certificado64 = self.__getCertificado64()
            certificadoX509 = self.__getCertificadox509(certificado64)
            # Calcula el número de serie del certificado y lo convierte en formato hexadecimal.
            self.__nocertificadoHex = hex(certificadoX509.get_serial_number())
            # Obtiene el número de certificado usando el número de serie en formato hexadecimal
            noCertificado = self.__getNoCertificado(self.__nocertificadoHex)

            # Agrega atributos al elemento raíz del árbol XML que representan la fecha, el número de certificado y el certificado en formato base64.
            arbol.attrib['Fecha'] = fecha
            arbol.attrib['NoCertificado'] = noCertificado
            arbol.attrib['Certificado'] = certificado64

            # Define un espacio de nombres para XPath.
            namespace = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

            # Utiliza XPath para buscar y obtener los elementos "Emisor" y "Receptor" del XML.
            xpath_Emisor = "//cfdi:Emisor"
            xpath_Receptor = "//cfdi:Receptor" 
            elementoEmisor = arbol.xpath(xpath_Emisor, namespaces=namespace)
            elementoReceptor = arbol.xpath(xpath_Receptor, namespaces=namespace)
           
            # Extrae el RFC (Registro Federal de Contribuyentes) tanto del emisor como del receptor y los almacena en las variables self.rfcEmisor y self.rfcReceptor, respectivamente.
            for element in elementoEmisor:
                self.rfcEmisor = element.attrib['Rfc']
            for element in elementoReceptor:
                self.rfcReceptor = element.attrib['Rfc']

            # Obtiene el tipo de comprobante del atributo 'TipoDeComprobante' del elemento raíz
            self.tipoDeComprobante = arbol.attrib['TipoDeComprobante']

            # Calcula la cadena original del comprobante utilizando algún método interno (__getCadenaOriginal), que probablemente siga las reglas específicas del Servicio de Administración Tributaria (SAT) en México.
            cadenaOriginal = self.__getCadenaOriginal(arbol)

            # Calcula el sello digital del comprobante utilizando algún método interno (__getSello), que probablemente utilice el certificado y la cadena original.
            sello = self.__getSello(cadenaOriginal)
            
            # Agrega el sello digital al atributo 'Sello' del elemento raíz del árbol XML.
            arbol.attrib['Sello'] = sello

            # Retorna la representación en bytes del árbol XML modificado.
            return etree.tostring(arbol, encoding="utf-8")

        except Exception as e:
            # Si ocurre alguna excepción durante este proceso, se registra un mensaje de advertencia y se eleva una excepción con el mensaje indicando que el comprobante no ha sido sellado.
            log.warn(f"CERT: {e}\n")
            raise Exception("El comprobante no ha sido sellado.")

    def __getCertificadoPem(self):
        with open(self._getPathCertificadoPem, 'rb') as f:
            dataCert = f.read()
        return dataCert

    def __getCertificado64(self):
        with open(self._getPathCertificado, 'rb') as f:
            datacert = f.read()
        cert64 = base64.b64encode(datacert)
        return cert64.decode('utf-8')

    def __getCertificadox509(self, certificado64):
        cert64string = re.sub('(.{64})', '\\1\n', certificado64, 0, re.DOTALL)
        cert64WithBE = self.BEGIN_CERTIFICATE + cert64string + self.END_CERTIFICATE
        certificado = crypto.load_certificate(crypto.FILETYPE_PEM, cert64WithBE.encode("ISO-8859-1"))
        return certificado

    def __getNoCertificado(self, serialHex):
        noCertificado = ''
        serialStr = str(serialHex)
        if ( len(serialStr) % 2 ) == 1 :
            serialStr = ' ' + serialStr
        serialLen = len(serialStr) // 2
        for index in range(serialLen):
            startIndex = (index * 2)
            endIndex = startIndex + 2
            aux = serialStr[startIndex:endIndex]     
            if 'x' != aux[1]:
                noCertificado = noCertificado + aux[1]
        return noCertificado

    def __getCadenaOriginal(self, arbol):
        xslt = etree.parse(self._getPathXLST)
        tranformar = etree.XSLT(xslt)
        cadenaOriginal = tranformar(arbol)
        return str(cadenaOriginal)
    
    def __getSello(self, cadenaOriginal):
        with open (self._getPathKey, 'r') as f:
            self.__privateKey = RSA.importKey(f.read())

        #Transaccion
        digestion = SHA256.new()
        digestion.update(str(cadenaOriginal).encode('utf-8'))
        
        #Signature
        firmante = PKCS1_v1_5.new(self.__privateKey) 
        firma = firmante.sign(digestion)
        return base64.b64encode(firma).decode('utf-8')