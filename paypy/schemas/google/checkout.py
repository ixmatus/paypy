from paypy.schemas.google      import IGoogleTransaction, IMerchantAuthentication
from zope.interface            import Interface, implements
from zope.schema               import Object
from zope.schema.fieldproperty import FieldProperty

class ICheckout(Interface):
    """Represents an AIM interface."""
    
    authentication = Object(title=u'Merchant Authentication',     description=u'Represents merchant authentication values.', schema=IMerchantAuthentication, required=True)
    transaction    = Object(title=u'Google Checkout Transaction', description=u'Represents a Google transaction',            schema=IGoogleTransaction,      required=True)
    
class SCheckout(object):
    """Reifier of an aim schema object."""
    
    implements(ICheckout)
    
    authentication = FieldProperty(ICheckout['authentication'])
    transaction    = FieldProperty(ICheckout['transaction'])
    
    def __repr__(self):
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))
