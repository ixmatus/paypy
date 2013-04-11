import re
from paypy.schemas.transaction import ITransaction, STransaction
from paypy.schemas.payment     import IPayment
from paypy.schemas.billing     import IBilling
from paypy.schemas.shipping    import IShipping

from zope.interface            import Interface, implements
from zope.schema               import TextLine, Object, Choice, Int, List, Bool
from zope.schema.fieldproperty import FieldProperty

NUMERIC    = re.compile('^[0-9]+$')
ALPHA      = re.compile('^[a-zA-Z0-9_\-.,\s]+$')
CURRENCY   = re.compile('^[0-9]+.[0-9][0-9]$')
INCLUSIVE  = re.compile('^[1-9]+%')
DECIMAL    = re.compile('(?!^0*$)(?!^0*\.0*$)^\d{1,5}(\.\d{1,2})?$')

# Merchant authentication schema
class IMerchantAuthentication(Interface):
    """Represents an Google merchant authentication."""
    
    id  = TextLine(title=u'Merchant ID', description=u'The merchant\'s unique API Login ID', required=True)
    key = TextLine(title=u'Merchant Key', description=u'The merchant\'s unique Transaction Key', required=True) # tran_key

class SMerchantAuthentication(object):
    """Reifier for an Google merchant authentication object."""
    
    implements(IMerchantAuthentication)
    
    id  = FieldProperty(IMerchantAuthentication['id'])
    key = FieldProperty(IMerchantAuthentication['key'])
    
    def __repr__(self):
        rep = ''
        
        if self.login:
            rep += self.login + ' '
        if self.key:
            rep += self.key + ' '
        
        return '<%s at 0x%x; %s>' % (self.__class__.__name__, abs(id(self)), rep)

# Sub-transaction schemas
class ITax(IItem):
    pass
class STax(SItem):
    implements(ITax)
    
    pass

class IItem(Interface):
    id          = TextLine(title=u'Item ID',     description=u'Line Item ID',        required=True)
    name        = TextLine(title=u'Name',        description=u'Name of item',        required=False)
    description = TextLine(title=u'Description', description=u'Description of item', required=True)
    quantity    = Int(title=u'Quantity',         description=u'Item quantity',       required=True, constraint=INCLUSIVE.match, min_length=1)
    price       = TextLine(title=u'Unit Price',  description=u'Cost of an item per unit excluding tax.', required=False, constraint=CURRENCY.match)
    weight      = TextLine(title=u'Weight',      description=u'Item weight',         required=False, constraint=DECIMAL.match)

class SItem(object):
    implements(IItem)
    
    id          = FieldProperty(IItem['id'])
    name        = FieldProperty(IItem['name'])
    description = FieldProperty(IItem['description'])
    quantity    = FieldProperty(IItem['quantity'])
    price       = FieldProperty(IItem['price'])
    weight      = FieldProperty(IItem['weight'])

# Base transaction schema
class IGoogleTransaction(ITransaction):
    """Represents a Google Checkout interface."""
    
    # Required fields
    items = List(title=u'Items', description=u'List of checkout items', value_type=Object(schema=IItem), required=False)
    
class SGoogleTransaction(STransaction):
    """Reifier of a google transaction schema object."""
    
    implements(IGoogleTransaction)
    
    items = FieldProperty(IGoogleTransaction['items'])

    def __repr__(self):
        
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))
