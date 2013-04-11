from paypy.schemas.authnet     import IAuthnetTransaction, IMerchantAuthentication
from zope.interface            import Interface, implements
from zope.schema               import Object
from zope.schema.fieldproperty import FieldProperty

class IAim(Interface):
    """Represents an AIM interface."""
    
    authentication = Object(title=u'Merchant Authentication',   description=u'Represents merchant authentication values.', schema=IMerchantAuthentication, required=True)
    transaction    = Object(title=u'Authorize.net Transaction', description=u'Represents an authorize.net transaction',    schema=IAuthnetTransaction,     required=True)
    
class SAim(object):
    """Reifier of an aim schema object."""
    
    implements(IAim)
    
    authentication = FieldProperty(IAim['authentication'])
    transaction    = FieldProperty(IAim['transaction'])
    
    def __repr__(self):
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))
