import logging, sys, hashlib, base64, os, re
from lxml import etree
from business.archivo import ArchivoService, ArchivoServiceError
from business.certificado import CertificadoService
from data.documento import MetadatoRepository
from model.comprobante import Comprobante, StatusComprobante
from datetime import datetime

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s %(message)s',
    stream = sys.stderr 
)
log = logging.getLogger('')

class DocumentoServiceError(Exception):
    def __init__(self, mensaje="Ocurrió un error."):
            self.mensaje = mensaje
            super().__init__(self.mensaje)

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
            log.warn(f"B2B: {e}\n")
            raise Exception("Han ocurrido errores en el servicio.")

    def __getMetadatoRepository(self):
        if self.__dataMetadatoRepository is not None:
            return self.__dataMetadatoRepository
        else:
            log.warn(f"B2B: {e}\n")
            raise Exception("El repositorio no esta disponible.")

    def __getCertificadoService(self):
        if self.__certificadoService is not None:
            return self.__certificadoService
        else:
            log.warn(f"B2B: {e}\n")
            raise Exception("El servicio de certificación no esta disponible.")

    def _firmarCancelacion(self, xmlPath):
        try:
            xmlCancelacionData = self.__getCertificadoService().cancelar(xmlPath)
            return xmlCancelacionData
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("El comprobante no ha sido firmado.")
    
    def _firmarComprobante(self, xmlPath):
        try:
            # representación en bytes del árbol XML modificado.
            data_cfdi = self.__getCertificadoService().sellar(xmlPath)         
            return data_cfdi
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("El comprobante no ha sido firmado.")

    def getAllDocumentos(self):
        comprobantes = []
        try:
           documentos = self.__getMetadatoRepository().doSelect()
           for documento in documentos:
                del documento['cfdiXml']
                c = Comprobante(**documento)
                c.cfdiXml = None
                comprobantes.append(c.dict())
           return comprobantes
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La búsqueda de los comprobante no fue exitosa.")
        
    def getDocumento(self, nombre):
        try:
            documento = self.__getMetadatoRepository().findComprobanteByNombre(nombre)
            if documento is None :
                errorComprobante = StatusComprobante(**{
                        'codigo':'001',
                        'descripcion':'El comprobante no ha sido encontrado.',
                        'descripcionTecnica':'',
                        'resultado':False
                        }
                    )
                log.warn(f"B2B: No se ha encontrado: {nombre}\n")
                return errorComprobante.dict()
            else:
                comprobante = Comprobante(**documento)
                # comprobante.cfdiXml = None
                log.info(f"B2B: Se ha encontrado: {documento['_id']}\n")
                return comprobante.dict()
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception("La búsqueda del comprobante no fue exitosa.")

    def setDocumento(self, archivo):
        nombre = hashlib.new(name="sha256", data=archivo).hexdigest()
        xmlPath = os.path.join(self.__repositoriopath,nombre) 
        try:
            #Guardar en Disco el XML
            archivoServiceTemp = ArchivoService(xmlPath)
            archivoServiceTemp.setArchivo(data=archivo)
            
            documentob64 = archivoServiceTemp.getArchivo()
            documentoData = base64.b64decode(documentob64)
            documentoStr = documentoData.decode('ISO-8859-1')

            patronComprobante = r"cfdi:Comprobante"
            patronCancelacion = r"Cancelacion"
            
            if len(re.findall(patronComprobante, documentoStr)) > 1:
                data_cfdi = self._firmarComprobante(xmlPath)
                str_cfdi = data_cfdi.decode('ISO-8859-1')
                patronTipoComprobante = r"(TipoDeComprobante)=(\"[A-Z]{1}\")"
                listTipo = re.findall(patronTipoComprobante, str_cfdi)
                if len(listTipo) > 0 :
                    tupla = listTipo[0]
                    tipoComprobante = tupla[1].replace("\"","")
                    archivoServiceCfdi = ArchivoService(f"{xmlPath}.xml")
                    archivoServiceCfdi.setArchivo(data=data_cfdi)
                    xml = archivoServiceCfdi.getArchivo()
                    comprobante = Comprobante(
                        estatus=0,
                        nombre=nombre,
                        rfcEmisor=self.__getCertificadoService().getRfcEmisor(),
                        rfcReceptor=self.__getCertificadoService().getRfcReceptor(),
                        cfdiXml=xml,
                        cadenaOriginal=self.__getCertificadoService()._getCadenaOriginal(),
                        timbreFiscal='',
                        sError='',
                        fechaEmision=str(datetime.now().isoformat())[:19],
                        idTipoDocumento=tipoComprobante)
                    
                    id = self.__getMetadatoRepository().doInsert(comprobante)
                    log.info(f"El comprobante han sido almacenado en el repositorio. {id}") 
                    return comprobante.dict()
                else:
                    raise Exception("No existe el Tipo de Comprobante.")
                
            elif len(re.findall(patronCancelacion, documentoStr)) > 1:
                xmlCancelacionData = self._firmarCancelacion(xmlPath)
                archivoServiceCancelacion = ArchivoService(f"{xmlPath}.xml")
                archivoServiceCancelacion.setArchivo(data=xmlCancelacionData)
                xmlCancelacionB64 = archivoServiceCancelacion.getArchivo()
                comprobante = Comprobante(
                    estatus=0,
                    nombre=nombre,
                    rfcReceptor='',
                    rfcEmisor='',
                    cfdiXml=xmlCancelacionB64,
                    cadenaOriginal='',
                    timbreFiscal='',
                    sError='',
                    fechaEmision=str(datetime.now().isoformat())[:19],
                    idTipoDocumento="C",
                    )

                id = self.__getMetadatoRepository().doInsert(comprobante)
                log.info(f"El comprobante han sido almacenado en el repositorio. {id}") 
                return comprobante.dict()
            else:
                errorComprobante = StatusComprobante(**{
                        'codigo':'001',
                        'descripcion':'El comprobante no es valido.',
                        'descripcionTecnica':'',
                        'resultado':False
                        }
                    )
                return errorComprobante.dict()
        except ArchivoServiceError as e:
            log.warn(f"B2B: Se ha generado una excepción en el servicio de archivos.\n")
            raise Exception(str(e))
        
        except Exception as e:
            archivoServiceTemp = ArchivoService(xmlPath)
            log.info("Los metadatos han sido eliminados del repositorio.")                
            archivoServiceTemp.deleteArchivo()
            log.info("El archivo ha sido eliminado del disco.")
            log.warn(f"B2B: {e}\n")
            raise Exception(e)
            # raise Exception("La carga de los comprobante no fue exitosa.")
    
    def updateDocumento(self, comprobante):
        try:
            # nombre = hashlib.new(name="sha256", data=archivo).hexdigest()
            comprobante['timbreFiscal']= "0000-00-00T00:00:00"
            documento = self.__getMetadatoRepository().doUpdate(comprobante)
            compro = Comprobante(**documento)
            # del documento['cfdiXml']
            # comprobante.cfdiXml = None
            return compro.dict()
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception(str(e))
        
    def deleteDocumento(self, nombre):
        try:
            try:
                documento = self.__getMetadatoRepository().doDelete(nombre)
                xmlPath = os.path.join(self.__repositoriopath,nombre) 
                archivoServiceTemp = ArchivoService(xmlPath)
                log.info("Los metadatos han sido eliminados del repositorio.")                
                archivoServiceTemp.deleteArchivo()
                log.info("El archivo ha sido eliminado del disco.")
                c = Comprobante(**documento)
                c.cfdiXml = None
                return c.dict()
            except Exception as e:
                errorComprobante = StatusComprobante(**{
                'codigo':'001',
                'descripcion':'El comprobante no ha sido eliminado.',
                'descripcionTecnica':'',
                'resultado':True
                })
                raise DocumentoServiceError(errorComprobante.dict())
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception(str(e))