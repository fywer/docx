import logging, sys, hashlib, base64, os, re
from lxml import etree
from business.archivo import ArchivoService
from business.certificado import CertificadoService
from data.documento import MetadatoRepository
from model.comprobante import Comprobante, ErrorComprobante
from datetime import datetime

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')
class DocumentoService: 
    __certpath = r'./server/config/EKU9003173C9.cer'
    __llavepath = r'./server/config/EKU9003173C9.key'
    __repositoriopath = os.path.join("M:")
    
    def __init__(self):
        self.__dataMetadatoRepository = None
        self.__certificadoService = None
        
        try:
            self.__dataMetadatoRepository = MetadatoRepository()
            self.__certificadoService = CertificadoService(certificado=self.__certpath, llave=self.__llavepath)
        except Exception as e :
            raise Exception("Han ocurrido errores en el servicio.")

    def __getMetadatoRepository(self):
        if self.__dataMetadatoRepository is not None:
            return self.__dataMetadatoRepository
        else:
            raise Exception("El repositorio no esta disponible.")

    def __getCertificadoService(self):
        if self.__certificadoService is not None:
            return self.__certificadoService
        else:
            raise Exception("El servicio de certificación no esta disponible.")

    def _firmarCancelacion(self, xmlPath, nombre):
        try:
            xmlCancelacionData = self.__getCertificadoService().cancelar(xmlPath)
            archivoServiceCancelacion = ArchivoService(f"{xmlPath}.xml")
            archivoServiceCancelacion.setArchivo(data=xmlCancelacionData)
            xmlCancelacionB64 = archivoServiceCancelacion.getArchivo()
            comprobante = Comprobante(
                estatus=1,
                RFCEmisor='',
                RFCReceptor='',
                UUID='',
                idTipoDocumento=0,
                nombre=nombre,
                tamanio=archivoServiceCancelacion.getTamanio(),
                fechaEmision=str(datetime.now().isoformat())[:19],
                cfdi=xmlCancelacionB64
                )
            return comprobante
        
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("El comprobante no ha sido firmado")
    
    tipoComprobanteToid  = lambda tipoComprobante: 1 if tipoComprobante == 'I' else (2 if tipoComprobante == 'E' else (99 if tipoComprobante == 'T' else (6 if tipoComprobante == 'P' else 3)))

    def _firmarComprobante(self, xmlPath, nombre):
        try:
            cfdi = self.__getCertificadoService().sellar(xmlPath)
            archivoServiceCfdi = ArchivoService(f"{xmlPath}.xml")
            archivoServiceCfdi.setArchivo(data=cfdi)
            
            tipoComprobante = self.__getCertificadoService().getTipoComprobante()
            
            if tipoComprobante == 'I':
                idTipoDocumento = 1
            elif tipoComprobante == 'E':
                idTipoDocumento = 2
            elif tipoComprobante == 'T':
                idTipoDocumento = 99
            elif tipoComprobante == 'P':
                idTipoDocumento = 6
            elif tipoComprobante == 'N':
                idTipoDocumento = 3
            xml = archivoServiceCfdi.getArchivo()
            comprobante = Comprobante(
                estatus=1,
                RFCEmisor=self.__getCertificadoService().getRfcEmisor(),
                RFCReceptor=self.__getCertificadoService().getRfcReceptor(),
                UUID='',
                idTipoDocumento=idTipoDocumento,
                nombre=nombre,
                tamanio=archivoServiceCfdi.getTamanio(),
                fechaEmision=str(datetime.now().isoformat())[:19],
                cfdi=xml
                )
             
            return comprobante
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("El comprobante no ha sido firmado.")

    def getAllDocumentos(self):
        comprobantes = []
        try:
           documentos = self.__getMetadatoRepository().doSelect()
           for documento in documentos:
                del documento['cfdi']
                c = Comprobante(**documento)
                c.cfdi = None
                comprobantes.append(c.dict())
           return comprobantes
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La búsqueda de los comprobante no fue exitosa.")
        
    def getDocumento(self, nombre):
        try:
            documento = self.__getMetadatoRepository().findComprobanteByNombre(nombre)
            if documento is None :
                errorComprobante = ErrorComprobante(**{'codigo':'001','info':'El comprobante no ha sido encontrado.'})
                log.warn(f"B2B: No se ha encontrado: {nombre}\n")
                return errorComprobante.dict()
            else:
                comprobante = Comprobante(**documento)
                comprobante.cfdi = None
                log.info(f"B2B: Se ha encontrado: {documento['_id']}\n")
                return comprobante.dict()
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La búsqueda del comprobante no fue exitosa.")

    def setDocumento(self, archivo):
        try:
            nombre = hashlib.new(name="sha256", data=archivo).hexdigest()
            xmlPath = os.path.join(self.__repositoriopath,nombre) 
            #Guardar en Disco el XML
            archivoServiceTemp = ArchivoService(xmlPath)
            archivoServiceTemp.setArchivo(data=archivo)
            documentoData = base64.b64decode(archivoServiceTemp.getArchivo())
            documento = documentoData.decode('ISO-8859-1')
            patronComprobante = r"cfdi:Comprobante"
            patronCancelacion = r"Cancelacion"
            if len(re.findall(patronComprobante, documento)) > 1:
                model_comprobante = self._firmarComprobante(xmlPath, nombre)
                id = self.__getMetadatoRepository().doInsert(model_comprobante)
                log.info(f"El comprobante han sido almacenado en el repositorio. {id}") 
                return model_comprobante.dict()
            elif len(re.findall(patronCancelacion, documento)) > 1:
                model_comprobante = self._firmarCancelacion(xmlPath, nombre)
                id = self.__getMetadatoRepository().doInsert(model_comprobante)
                log.info(f"El comprobante han sido almacenado en el repositorio. {id}") 
                return model_comprobante.dict()
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La carga de los comprobante no fue exitosa.")
    
    def updateDocumento(self, comprobante, archivo):
        try:
            nombre = hashlib.new(name="sha256", data=archivo).hexdigest()
            comprobante['nombre'] = nombre
            documento = self.__getMetadatoRepository().doUpdate(nombre, comprobante)
            comprobante = Comprobante(**documento)
            del documento['cdfi']
            comprobante.cfdi = None
            return comprobante.dict()
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La actualizacion del comprobante no fue exitosa.")
    
    def deleteDocumento(self, nombre):
        try:
            documento = self.__getMetadatoRepository().doDelete(nombre)
            if documento is None :
                errorComprobante = ErrorComprobante(**{'codigo':'002','info':'El comprobante no ha sido eliminado.'})
                log.warn(f"B2B: No se ha eliminado: {nombre}\n")
                return errorComprobante.dict()
            else:
                xmlPath = os.path.join(self.__repositoriopath,nombre) 
                archivoServiceTemp = ArchivoService(xmlPath)
                log.info("Los metadatos han sido eliminados del repositorio.")                
                archivoServiceTemp.deleteArchivo()
                log.info("El archivo ha sido eliminado del disco.")
                c = Comprobante(**documento)
                c.cfdi = None
                return c.dict()
        
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("El comprobante no ha sido eliminado.")