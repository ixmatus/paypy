import urllib2

from lxml import etree as ET

from paypy.adapters                import *
from paypy.exceptions.authnet      import ARBException
from paypy.schemas.authnet.arb     import IAuthnetSubscriptionCreate, IAuthnetSubscriptionUpdate, IAuthnetSubscriptionStatus, IAuthnetSubscriptionCancel
from paypy.serializers.authnet.arb import Serialize
from paypy.schemas.authnet.arb     import IArb

ARB_REQUEST_ELEMENTS    = {'create' : 'ARBCreateSubscriptionRequest',
                           'update' : 'ARBUpdateSubscriptionRequest',
                           'status' : 'ARBGetSubscriptionStatusRequest',
                           'cancel' : 'ARBCancelSubscriptionRequest'}

class RecurringTransactionResult(Result):
    """Represent a recurring (subscription) transaction result as an object."""
    
    def __init__(self, data):
        """Set the result items."""
        
        ANET_XMLNS = ' xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd"'
        
        data     = data.replace(ANET_XMLNS, '')
        
        root     = ET.XML(data)
        messages = root.find('messages')
        
        self.result_code = messages.find('resultCode').text
        self.code        = messages.find('message/code').text
        self.reason      = messages.find('message/text').text
        self.status      = None
        
        self.subscription_id = None
        subscription_id      = root.find('subscriptionId')
        
        if root.tag == 'ARBCreateSubscriptionResponse' and subscription_id is not None:
            self.subscription_id = subscription_id.text
        
        # GetSubscriptionStatusResponse specific
        if root.tag == 'ARBGetSubscriptionStatusResponse':
            self.status = root.find('Status').text.capitalize().strip()
    
    def __str__(self):
        """Calling str on the object will return the subscription_id if successful (and it exists) or the the message."""
        
        if self.subscription_id:
            return self.subscription_id
        
        if self.status:
            return self.status
        
        return self.reason
    
    def __repr__(self):
        """Object representation of the subscription result object."""
        
        return '<%s at 0x%x %s>' % (self.__class__.__name__, abs(id(self)), self.result_code)

class RecurringTransaction(Adapter):
    """Authorize.net ARB (Automated Recurring Billing) transaction object adapter.
    
    Represent an Authorize.net recurring transaction and provide
    methods for submitting new subscriptions, updating subscriptions,
    cancelling subscriptions, and retrieving the status of a
    subscription.
    
    """
    
    def __init__(self, options):
        
        ENDPOINT_XML_PRODUCTION = 'api.authorize.net/xml/v1/'
        ENDPOINT_XML_TEST       = 'apitest.authorize.net/xml/v1/'
        REQUEST_PATH            = 'request.api'
        
        if not IArb.providedBy(options):
            raise ARBException('the options object must provide a valid schema interface')
        
        self.options    = options
        self.serialized = Serialize(options)
        
        testing = options.subscription.testing
        host    = ENDPOINT_XML_TEST if testing else ENDPOINT_XML_PRODUCTION
        
        self.connection = urllib2.Request(url='https://' + host + REQUEST_PATH, headers={'Content-Type' : 'text/xml'})
    
    def create(self):
        """Create a new subscription."""
        
        if not IAuthnetSubscriptionCreate.providedBy(self.options.subscription):
            raise ARBException('a creation request must conform to the IAuthnetSubscriptionCreate interface')
        
        return RecurringTransactionResult(self._request())
    
    def update(self):
        """Update a given subscription."""
        
        if not IAuthnetSubscriptionUpdate.providedBy(self.options.subscription):
            raise ARBException('an update request must conform to the IAuthnetSubscriptionUpdate interface')
        
        return RecurringTransactionResult(self._request())
    
    def status(self):
        """Retrieve the subscription's status."""
        
        if not IAuthnetSubscriptionStatus.providedBy(self.options.subscription):
            raise ARBException('a status request must conform to the IAuthnetSubscriptionStatus interface')
        
        return RecurringTransactionResult(self._request())
    
    def cancel(self):
        """Cancel the subscription object."""
        
        if not IAuthnetSubscriptionCancel.providedBy(self.options.subscription):
            raise ARBException('a cancel request must conform to the IAuthnetSubscriptionCancel interface')
        
        return RecurringTransactionResult(self._request())
    
    def _request(self):
        """Send the request to authorize.net."""
        
        data = str(self.serialized)
        
        print data
        
        self.connection.headers['Content-Length'] = str(len(data))
        self.connection.data                      = data
        
        request   = urllib2.urlopen(self.connection)
        result    = request.read()
        
        return result
