import re

from zope.interface            import Interface, implements
from zope.schema               import TextLine, Choice, Datetime
from zope.schema.fieldproperty import FieldProperty

class IPayment(Interface):
    pass

class ICreditCard(IPayment):
    """Defines an interface for credit card payment types."""
    
    number     = TextLine(title=u'Credit Card PAN',             description=u'A valid credit card number',          required=True, constraint=re.compile('^[0-9X]+$').match, min_length=4, max_length=16)
    expiration = Datetime(title=u'Credit Card Expiration Date', description=u'A valid credit card expiration date', required=True)
    ccv        = TextLine(title=u'Card Code Validation',        description=u'A credit card, card code validation', required=False)
    type       = Choice(title=u'Credit Card Type',              description=u'A valid credit type',                 required=False, values=(u'visa', u'mastercard', u'discover', u'amex', u'jcb', u'dinersclubs'))

class IBank(IPayment):
    """Defines an interface for bank payment types."""
    
    account_number  = TextLine(title=u'Bank Account Number', description=u'A valid bank account number',        required=True)
    routing_number  = TextLine(title=u'Bank Routing Number', description=u'A valid bank routing number',        required=True)
    name            = TextLine(title=u'Bank Name',           description=u'Name of the account holder\'s bank', required=False)
    name_on_account = TextLine(title=u'Name on Account',     description=u'Account holder\'s name',             required=True)
    account_type    = Choice(title=u'Account Type',          description=u'Bank account type',                  required=False, values=(u'checking', u'savings', u'businessChecking'))
    echeck_type     = Choice(title=u'EChek Type',            description=u'ECheck Type',                        required=False, values=(u'CCD', u'PPD', u'TEL', u'WEB'))

class SCreditCard(object):
    """Reifier of a credit card schema object."""
    
    implements(ICreditCard)
    
    number     = FieldProperty(ICreditCard['number'])
    expiration = FieldProperty(ICreditCard['expiration'])
    ccv        = FieldProperty(ICreditCard['ccv'])
    type       = FieldProperty(ICreditCard['type'])
    
    def __repr__(self):
        return '<%s at 0x%x; %s %s>' % (self.__class__.__name__, abs(id(self)), self.number, self.expiration.strftime('%m/%Y'))

class SBank(object):
    """Reifier of a bank schema object."""
    
    implements(IBank)
    
    account_number  = FieldProperty(IBank['account_number'])
    routing_number  = FieldProperty(IBank['routing_number'])
    name_on_account = FieldProperty(IBank['name_on_account'])
    name            = FieldProperty(IBank['name'])
    account_type    = FieldProperty(IBank['account_type'])
    echeck_type     = FieldProperty(IBank['echeck_type'])
    
    def __repr__(self):
        return '<%s at 0x%x; %s %s>' % (self.__class__.__name__, abs(id(self)), self.routing_number, self.account_number)
