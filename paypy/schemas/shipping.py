from address        import IAddress, SAddress
from zope.interface import implements

class IShipping(IAddress):
    """Defines an interface for shipping profile types.
    
    Subclasses the IAddress interface.
    
    """
    
    pass

class SShipping(SAddress):
    """Reifier of a shipping profile schema object.
    
    Subclasses the Address schema.
    
    """
    
    implements(IShipping)
    
    def __repr__(self):
        return super(SShipping, self).__repr__()
