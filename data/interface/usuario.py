from abc import ABC, abstractmethod

class IUsuarioData(ABC):
    @abstractmethod
    def doInsert(self, usuario):
        pass

    @abstractmethod
    def doDelete(self, id):
        pass

    @abstractmethod
    def doSelect(self, id=False):
        pass