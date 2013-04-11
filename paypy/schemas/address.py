import re

from zope.interface            import Interface, implements
from zope.schema               import TextLine
from zope.schema.fieldproperty import FieldProperty

ALPHA = re.compile(r'^[\w\_\-\.,\(\)\[\]\s]+$', re.IGNORECASE | re.UNICODE)
ADDR  = re.compile(r'^[\w\_\-\#\.\/,\;\:\'\"\s]+$', re.IGNORECASE | re.UNICODE)

class IAddress(Interface):
    """Defines an interface for address types."""
    
    firstname   = TextLine(title=u'First Name',   description=u'Given name',           required=False, constraint=ALPHA.match, max_length=800)
    lastname    = TextLine(title=u'Last Name',    description=u'Family name',          required=False, constraint=ALPHA.match, max_length=800)
    company     = TextLine(title=u'Company Name', description=u'Company name',         required=False, constraint=ALPHA.match, max_length=800)
    address     = TextLine(title=u'Address',      description=u'Address',              required=False, constraint=ADDR.match, max_length=1000)
    city        = TextLine(title=u'City',         description=u'City of residence',    required=False, constraint=ALPHA.match, max_length=100)
    state       = TextLine(title=u'State',        description=u'State of residence',   required=False, constraint=ALPHA.match, max_length=800)
    country     = TextLine(title=u'Country',      description=u'Country of residence', required=False, constraint=ALPHA.match, max_length=1000)
    postal_code = TextLine(title=u'Postal Code',  description=u'Postal code',          required=False, constraint=ALPHA.match, max_length=100)
    phone       = TextLine(title=u'Phone Number', description=u'Phone number',         required=False, constraint=re.compile(r'^[0-9()-.,\s]+$').match, max_length=25)
    fax         = TextLine(title=u'Fax Number',   description=u'Fax number',           required=False, constraint=re.compile(r'^[0-9()-.,\s]+$').match, max_length=25)

class SAddress(object):
    """Reifier of an address schema object."""
    
    implements(IAddress)
    
    firstname   = FieldProperty(IAddress['firstname'])
    lastname    = FieldProperty(IAddress['lastname'])
    company     = FieldProperty(IAddress['company'])
    address     = FieldProperty(IAddress['address'])
    city        = FieldProperty(IAddress['city'])
    state       = FieldProperty(IAddress['state'])
    country     = FieldProperty(IAddress['country'])
    postal_code = FieldProperty(IAddress['postal_code'])
    phone       = FieldProperty(IAddress['phone'])
    fax         = FieldProperty(IAddress['fax'])
    
    def __repr__(self):
        rep = ''
        
        if self.firstname:
            rep += self.firstname + ' '
        if self.lastname:
            rep += self.lastname  + ' '
        
        return '<%s at 0x%x; %s>' % (self.__class__.__name__, abs(id(self)), rep)
