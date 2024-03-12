import logging, sys, hashlib, base64, os, re
from lxml import etree
from business.archivo import ArchivoService
from business.certificado import CertificadoService
from data.documento import MetadatoRepository
from model.comprobante import Comprobante
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
            # self.__dataMetadatoRepository = MetadatoRepository()
            
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

    def getAllDocumentos(self):
        try:
           documentos = self.__getMetadatoRepository().doSelect()
           return documentos
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La búsqueda de los comprobante no fue exitosa.")
        
    def getDocumento(self, id):
        try:
            documento = self.__getMetadatoRepository().doSelect(id)
            if documento is False:
                return
                {
                    "msg:": "No se han encontrado registros."
                }
            else:
                nombre = documento["nombre"]+".xml"
                documento["contenido"] = self.__getArchivoService().getArchivo(nombre) 
                documento["ruta"] = self.__getArchivoService().getRuta(nombre)
                return documento
        except Exception as e:
            raise Exception("ADVERTENCIA {0}".format(e))

    def deleteDocumento(self,id):
        try:
            metadata = self.__getMetadatoRepository().doSelect(id)
            self.__getMetadatoRepository().doSelect(metadata['id'])
            log.info("Los metadatos han sido eliminados en sqlserver.")                
            ruta = self.__getArchivoService().deleteArchivo(metadata['nombre'])
            log.info("El archivo ha sido eliminado en mysql.")
        except Exception as e:
            raise Exception(e)

    def firmarCancelacion(self, xmlPath, nombre):
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

    def firmarComprobante(self, xmlPath, nombre):
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
                
            self.__getMetadatoRepository().doInsert(metadata)
            log.info("Los metadatos han sido almacenados en SQLServer.") 

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
                return self.firmarComprobante(xmlPath, nombre)
            elif len(re.findall(patronCancelacion, documento)) > 1:
                return self.firmarCancelacion(xmlPath, nombre)
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La carga de los comprobante no fue exitosa.")