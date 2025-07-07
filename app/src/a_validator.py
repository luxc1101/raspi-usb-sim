from abc import ABC, abstractmethod

from .a_device import ADevice


class AValidator(ABC):
    
    @abstractmethod
    def validate(self, device:ADevice):
        pass

    @abstractmethod
    def repair(self, device:ADevice):
        pass