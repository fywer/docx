from abc import ABC, abstractmethod

class IDocumentoData(ABC):

    @abstractmethod
    def doInsert(self, documento):
        pass

    @abstractmethod
    def doDelete(self, id):
        pass

    @abstractmethod
    def doSelect(self, id=False):
        pass