from address                   import IAddress, SAddress

from zope.interface            import implements
from zope.schema               import Choice
from zope.schema.fieldproperty import FieldProperty

class IBilling(IAddress):
    """Defines an interface for billing profile types.
    
    Subclasses the IAddress interface.
    
    """
    
    entity_type = Choice(title=u'Entity type', description=u'Entity type', values=('individual', 'business'), default='individual')

class SBilling(SAddress):
    """Reifier of a billing profile schema object.
    
    Subclasses the Address schema.
    
    """
    
    implements(IBilling)
    entity_type = FieldProperty(IBilling['entity_type'])
    
    def __repr__(self):
        return super(SBilling, self).__repr__()
