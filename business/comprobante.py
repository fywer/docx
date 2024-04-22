import hashlib, base64, os, re, logging, sys
from business.archivo import ArchivoService, ArchivoServiceError
from business.certificado import CertificadoService
from data.comprobante import ComprobanteRepository
from model.comprobante import Comprobante, StatusComprobante
from datetime import datetime
from util.config import CONFIG
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

class ComprobanteService: 
    __repositorioPath = CONFIG["service.archivo"]["repositoriopath"]
    
    def __init__(self):
        self.__dataMetadatoRepository = None
        self.__certificadoService = None
        try:
            self.__dataMetadatoRepository = ComprobanteRepository()
            __certpath = CONFIG["service.certificado"]["publicpath"]
            __llavepath = CONFIG["service.certificado"]["privatepath"]
            self.__certificadoService = CertificadoService(cert=__certpath, key=__llavepath)
        except Exception as e :
            log.warn(f"B2B: {e}\n")
            raise Exception("Han ocurrido errores en el servicio de comprobantes.")
        
    def __getMetadatoRepository(self):
        if self.__dataMetadatoRepository is not None:
            return self.__dataMetadatoRepository
        else:
            raise Exception("El repositorio de comprobantes no esta disponible.")

    def __getCertificadoService(self):
        if self.__certificadoService is not None:
            return self.__certificadoService
        else:
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

    def getAllComprobantes(self):
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
            raise Exception("La búsqueda de los comprobante no ha sido exitosa.")
        
    def getComprobante(self, nombre):
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
            raise Exception("La búsqueda del comprobante no ha sido exitosa.")

    def setComprobante(self, archivo):
        documentoStr = archivo.decode('ISO-8859-1')
        patronComprobante = r"cfdi:Comprobante"
        patronCancelacion = r"Cancelacion"
        nombre = hashlib.new(name="sha256", data=archivo).hexdigest()
        try:
            if len(re.findall(patronComprobante, documentoStr)) > 1:
                xmlPath = os.path.join(self.__repositorioPath,nombre) 
                archivoServiceTemp = ArchivoService(xmlPath)
                archivoServiceTemp.setArchivo(data=archivo)

                data_cfdi = self._firmarComprobante(xmlPath)
                str_cfdi = data_cfdi.decode('ISO-8859-1')
                patronTipoComprobante = r"(TipoDeComprobante)=(\"[A-Z]{1}\")"
                patronRFC = r"(Rfc)=(\"[A-Z&Ñ]{3,4}[0-9]{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])[A-Z0-9]{2}[0-9A]\")"
                listTipo = re.findall(patronTipoComprobante, str_cfdi)
                listRfc = re.findall(patronRFC, str_cfdi)
                if len(listTipo) > 0 :
                    tupla = listTipo[0]
                    tipoComprobante = tupla[1].replace("\"","")
                    archivoServiceCfdi = ArchivoService(f"{xmlPath}.xml")
                    archivoServiceCfdi.setArchivo(data=data_cfdi)
                    xml = archivoServiceCfdi.getArchivo()
                    comprobante = Comprobante(
                        estatus=0,
                        nombre=nombre,
                        rfcEmisor=listRfc[0][1].replace("\"",""),
                        rfcReceptor=listRfc[1][1].replace("\"",""),
                        cfdiXml=xml,
                        cadenaOriginal=self.__getCertificadoService().getCadenaOriginal,
                        timbreFiscal='',
                        sError='',
                        fechaEmision=str(datetime.now().isoformat())[:19],
                        idTipoDocumento=tipoComprobante)
                    comp_dict = dict(comprobante)
                    id = self.__getMetadatoRepository().doInsert(comp_dict)
                    log.info(f"El comprobante han sido almacenado en el repositorio. {id}") 
                    return comprobante.dict()
                else:
                    raise Exception("No existe el tipo de comprobante.")
                
            elif len(re.findall(patronCancelacion, documentoStr)) > 1:
                xmlPath = os.path.join(self.__repositorioPath,nombre) 
                archivoServiceTemp = ArchivoService(xmlPath)
                archivoServiceTemp.setArchivo(data=archivo)
                xmlCancelacionData = self._firmarCancelacion(xmlPath)
                xmlCancelacionStr = xmlCancelacionData.decode('ISO-8859-1')
                archivoServiceCancelacion = ArchivoService(f"{xmlPath}.xml")
                archivoServiceCancelacion.setArchivo(data=xmlCancelacionData)
                xmlCancelacionB64 = archivoServiceCancelacion.getArchivo()
                patronRFCEmisor = r"(RfcEmisor)=(\"[A-Z&Ñ]{3,4}[0-9]{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])[A-Z0-9]{2}[0-9A]\")"
                listRfcEmi = re.findall(patronRFCEmisor, xmlCancelacionStr)
                comprobante = Comprobante(
                    estatus=0,
                    nombre=nombre,
                    rfcReceptor='',
                    rfcEmisor=listRfcEmi[0][1].replace("\"",""),
                    cfdiXml=xmlCancelacionB64,
                    cadenaOriginal='',
                    timbreFiscal='',
                    sError='',
                    fechaEmision=str(datetime.now().isoformat())[:19],
                    idTipoDocumento="C",
                    )
                comp_dict = dict(comprobante)
                id = self.__getMetadatoRepository().doInsert(comp_dict)
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
                raise ArchivoServiceError(errorComprobante.dict())
        
        except ArchivoServiceError as e:
            log.warn(f"B2B: Se ha generado una exepción en el servicio de archivos.\n")
            raise DocumentoServiceError(e)
        
        except Exception as e:
            log.warn(f"B2B: El comprobante no ha sido almacenado en el repositorio.\n")
            errorComprobante = StatusComprobante(**{
                'codigo':'001',
                'descripcion':'El comprobante no ha sido almacenado en el repositorio.',
                'descripcionTecnica':str(e),
                'resultado':False
            }
            )
            raise DocumentoServiceError(errorComprobante.dict())
    
    def updComprobante(self, comprobante):
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
        
    def delComprobante(self, nombre):
        try:
            try:
                documento = self.__getMetadatoRepository().doDelete(nombre)
                xmlPath = os.path.join(self.__repositorioPath,nombre) 
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
                'descripcionTecnica':f'{e}',
                'resultado':True
                })
                raise DocumentoServiceError(errorComprobante.dict())
        except Exception as e:
            log.warn(f"B2B: {e}\n")
            raise Exception(str(e))