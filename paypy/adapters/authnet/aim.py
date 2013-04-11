import urllib2
import hashlib

from paypy.adapters                import *
from paypy.exceptions.authnet      import AIMException

from paypy.serializers.authnet.aim import Serialize
from paypy.schemas.authnet.aim     import IAim

class TransactionResult(Result):
    """Represent a transaction result as an object."""
    
    def __init__(self, data, delimiter='|'):
        RESPONSE_CODES  = {
            1: 'approved',
            2: 'declined',
            3: 'error',
            4: 'held for review'
        }
        
        fields = data.split(delimiter)
        
        self.code             = int(fields[0])
        self.status           = RESPONSE_CODES[self.code]
        self.subcode          = int(fields[1])
        self.reason_code      = int(fields[2])
        self.reason           = fields[3]
        self.approval         = fields[4]  if fields[4]  != '' else None
        self.avs              = fields[5]  if fields[5]  != '' else None
        self.transaction_id   = fields[6]  if fields[6]  != '' else None
        self.invoice_id       = fields[7]  if fields[7]  != '' else None
        self.description      = fields[8]  if fields[8]  != '' else None
        self.amount           = fields[9]  if fields[9]  != '' else None
        self.method           = fields[10] if fields[10] != '' else None
        self.type             = fields[11] if fields[11] != '' else None
        self.customer_id      = fields[12] if fields[12] != '' else None
        self.firstname        = fields[13] if fields[13] != '' else None
        self.lastname         = fields[14] if fields[14] != '' else None
        self.company          = fields[15] if fields[15] != '' else None
        self.address          = fields[16] if fields[16] != '' else None
        self.city             = fields[17] if fields[17] != '' else None
        self.state            = fields[18] if fields[18] != '' else None
        self.zip              = fields[19] if fields[19] != '' else None
        self.country          = fields[20] if fields[20] != '' else None
        self.phone            = fields[21] if fields[21] != '' else None
        self.fax              = fields[22] if fields[22] != '' else None
        self.email            = fields[23] if fields[23] != '' else None
        self.ship_firstname   = fields[24] if fields[24] != '' else None
        self.ship_lastname    = fields[25] if fields[25] != '' else None
        self.ship_company     = fields[26] if fields[26] != '' else None
        self.ship_address     = fields[27] if fields[27] != '' else None
        self.ship_city        = fields[28] if fields[28] != '' else None
        self.ship_state       = fields[29] if fields[29] != '' else None
        self.ship_zip         = fields[30] if fields[30] != '' else None
        self.ship_country     = fields[31] if fields[31] != '' else None
        self.tax              = fields[32] if fields[32] != '' else None
        self.duty             = fields[33] if fields[33] != '' else None
        self.freight          = fields[34] if fields[34] != '' else None
        self.tax_exempt       = fields[35] if fields[35] != '' else None
        self.po_number        = fields[36] if fields[36] != '' else None
        self.hash             = fields[37] if fields[37] != '' else None
        self.ccr              = fields[38] if fields[38] != '' else None
        self.avr              = fields[39] if fields[39] != '' else None
        self.account_number   = fields[40] if fields[40] != '' else None
        self.card_type        = fields[41] if fields[41] != '' else None
        self.tender_id        = fields[42] if fields[42] != '' else None
        self.requested_amount = fields[43] if fields[43] != '' else None
        self.balance          = fields[44] if fields[44] != '' else None
        
        self.response         = fields
    
    def validate(self, login, salt):
        """Validate a returned response with the given hash."""
        
        value = ''.join([salt, login, self.transaction_id, self.amount])
        return self.hash.upper() == hashlib.md5(value).hexdigest().upper()
    
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
        ENDPOINT_AIM_PRODUCTION = 'secure.authorize.net/gateway/transact.dll'
        ENDPOINT_AIM_TEST       = 'test.authorize.net/gateway/transact.dll'
        
        if not IAim.providedBy(options):
            raise AIMException('the options object must provide a valid schema interface')
        
        self.options    = options
        self.serialized = Serialize(options)
        
        testing = options.transaction.testing
        host    = ENDPOINT_AIM_TEST if testing else ENDPOINT_AIM_PRODUCTION
        
        # Create the connection object
        self.connection = urllib2.Request(url='https://' + host)
    
    def process(self):
        """Process the transaction and return a result."""
        
        data = str(self.serialized)
        
        self.connection.headers['Content-Length'] = str(len(data))
        self.connection.data                      = data
        
        request = urllib2.urlopen(self.connection)
        result  = TransactionResult(request.read())
        
        return result
