import urllib2
import base64

from paypy.adapters                import *
from paypy.exceptions.google       import CheckoutException

from paypy.serializers.google.checkout import Serialize
from paypy.schemas.google.checkout     import ICheckout

class TransactionResult(Result):
    """Represent a transaction result as an object."""
    
    def __init__(self, data):
        pass
    
    def __str__(self):
        """Return the response message."""
        
        return self.reason
    
    def __int__(self):
        """Return the response code."""
        
        return self.code
    
    def __repr__(self):
        """Return the object representation."""
        
        return '<%s at 0x%x %s>' % (self.__class__.__name__, abs(id(self)), self.type)

class Transaction(Adapter):
    """Authorize.net AIM (Advanced Integration Method) transaction object adapter.
    
    Represent an Authorize.net transaction and provide a method for
    submission.
    
    """
    
    def __init__(self, options):
        ENDPOINT_CHECKOUT_PRODUCTION = 'checkout.google.com/api/checkout/v2/request/Merchant/'
        ENDPOINT_CHECKOUT_TEST       = 'sandbox.google.com/api/checkout/v2/request/Merchant/'
        
        if not ICheckout.providedBy(options):
            raise CheckoutException('the options object must provide a valid schema interface')
        
        self.options    = options
        self.serialized = Serialize(options)
        
        testing = options.transaction.testing
        host    = ENDPOINT_CHECKOUT_TEST if testing else ENDPOINT_CHECKOUT_PRODUCTION
        
        # Create the connection object
        self.connection = urllib2.Request(url='https://' + host + self.options.auth.merchant_id)
    
    def process(self):
        """Process the transaction and return a result."""
        
        data = str(self.serialized)
        
        self.connection.headers['Content-Length'] = str(len(data))
        
        # We need to build the HTTP Basic Auth headers here
        self.connection.headers['Content-Type']   = 'application/xml; charset=UTF-8'
        self.connection.headers['Accept']         = 'application/xml; charset=UTF-8'
        self.connection.headers['Authorization']  = base64.b64encode("%s:%s" % (self.options.auth.merchant_id, self.options.auth.merchant_key))
        
        self.connection.data                      = data
        
        request = urllib2.urlopen(self.connection)
        result  = TransactionResult(request.read())
        
        return result
