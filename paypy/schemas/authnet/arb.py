import datetime
import re

from paypy.schemas             import billing, shipping, transaction
from paypy.schemas.payment     import IPayment
from paypy.schemas.authnet     import IMerchantAuthentication
from zope.interface            import Interface, implements
from zope.schema               import Object, TextLine, Int, Choice, Datetime
from zope.schema.fieldproperty import FieldProperty

ALPHA      = re.compile(r'^[\w\-.,\s]+$', re.IGNORECASE | re.UNICODE)
CURRENCY   = re.compile(r'^[0-9]+.[0-9][0-9]$')

# Super parent interfaces
class IAuthnetSubscription(transaction.ITransaction):
    pass
class SAuthnetSubscription(transaction.STransaction):
    implements(IAuthnetSubscription)

# Primary ARB interface object
class IArb(Interface):
    """Represents an AIM interface."""
    
    authentication = Object(title=u'Merchant Authentication',   description=u'Represents merchant authentication values.', schema=IMerchantAuthentication, required=True)
    subscription   = Object(title=u'Authorize.net Recurring Billing', description=u'Represents an authorize.net recurring billing request', schema=IAuthnetSubscription, required=True)
    
class SArb(object):
    """Reifier of an aim schema object."""
    
    implements(IArb)
    
    authentication = FieldProperty(IArb['authentication'])
    subscription   = FieldProperty(IArb['subscription'])
    
    def __repr__(self):
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))

class ISchedule(Interface):
    """Represents an ARB Schedule block interface."""
    
    length       = Int(title=u'Interval Length',     description=u'The measurement of time, in association with the Interval Unit, that is used to define the frequency of the billing occurrences.', max=365, required=True, default=1)
    unit         = Choice(title=u'Interval Units',   description=u'The unit of time, in association with the Interval Length, between each billing occurrence.', values=('months', 'days'), default='months', required=True)
    start        = Datetime(title=u'Interval Start', description=u'The date the subscription begins (also the date the initial billing occurs).', required=True, default=datetime.datetime.utcnow())
    cycles       = Int(title=u'Total Occurrences',   description=u'Number of billing occurrences or payments for the subscription.', min=1, max=9999, required=True, default=9999)
    trial_cycles = Int(title=u'Trial Occurrences',   description=u'Number of billing occurrences or payments in the trial period.', min=1, max=99, required=False)

class SSchedule(object):
    """Reifier for an ARB Schedule block object."""
    
    implements(ISchedule)
    
    length       = FieldProperty(ISchedule['length'])
    unit         = FieldProperty(ISchedule['unit'])
    start        = FieldProperty(ISchedule['start'])
    cycles       = FieldProperty(ISchedule['cycles'])
    trial_cycles = FieldProperty(ISchedule['trial_cycles'])

    def __repr__(self):
        return '<%s at 0x%x; %s>' % (self.__class__.__name__, abs(id(self)), self.start)

class IAuthnetSubscriptionWrite(IAuthnetSubscription):
    """Parent to create and update schemas."""
    
    ref_id       = TextLine(title=u'Reference ID',      description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    name         = TextLine(title=u'Subscription Name', description=u'Merchant-assigned name for the subscription.', max_length=50, required=False)
    description  = TextLine(title=u'Subscription description', description=u'Merchant assigned description of the subscription.', max_length=255, required=False)
    amount       = TextLine(title=u'Billing Amount',    description=u'The amount to be billed to the customer for each payment in the subscription.', max_length=15, constraint=CURRENCY.match, required=True)
    trial_amount = TextLine(title=u'Trial Billing Amount', description=u'The amount to be charged for each payment during a trial period.', max_length=15, constraint=CURRENCY.match, required=False)
    invoice      = TextLine(title=u'Invoice ID', description=u'Merchant-assigned invoice number for the subscription.', max_length=20, required=False)
    customer_id  = TextLine(title=u'Customer ID', description=u'Merchant-assigned identifier for the customer.', max_length=20, required=False)
    email        = TextLine(title=u'Customer\'s Email', description=u'The customer\'s email address.', max_length=255, required=False)
    billing      = Object(title=u'Billing Address', description=u'The customer\'s billing address', schema=billing.IBilling, required=False)
    shipping     = Object(title=u'Shipping Address', description=u'The customer\'s shipping address', schema=shipping.IShipping, required=False)
    schedule     = Object(title=u'Subscription Schedule', description=u'The billing schedule for the subscription.', schema=ISchedule, required=True)
    
    # Since payment can be either credit card or bank, we don't specify a schema type constraint, but we should - I may do this with a parent class in the future
    payment      = Object(title=u'Payment', description=u'Payment options', schema=IPayment, required=True)

class SAuthnetSubscriptionWrite(SAuthnetSubscription):
    implements(IAuthnetSubscriptionWrite)
    
    ref_id       = FieldProperty(IAuthnetSubscriptionWrite['ref_id'])
    name         = FieldProperty(IAuthnetSubscriptionWrite['name'])
    description  = FieldProperty(IAuthnetSubscriptionWrite['description'])
    amount       = FieldProperty(IAuthnetSubscriptionWrite['amount'])
    trial_amount = FieldProperty(IAuthnetSubscriptionWrite['trial_amount'])
    invoice      = FieldProperty(IAuthnetSubscriptionWrite['invoice'])
    customer_id  = FieldProperty(IAuthnetSubscriptionWrite['customer_id'])
    email        = FieldProperty(IAuthnetSubscriptionWrite['email'])
    billing      = FieldProperty(IAuthnetSubscriptionWrite['billing'])
    shipping     = FieldProperty(IAuthnetSubscriptionWrite['shipping'])
    schedule     = FieldProperty(IAuthnetSubscriptionWrite['schedule'])
    payment      = FieldProperty(IAuthnetSubscriptionWrite['payment'])

class IAuthnetSubscriptionRead(IAuthnetSubscription):
    id     = TextLine(title=u'Subscription ID', description=u'The subscription\'s ID.', max_length=13, required=True)
    ref_id = TextLine(title=u'Reference ID',    description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)

class SAuthnetSubscriptionRead(SAuthnetSubscription):
    implements(IAuthnetSubscriptionRead)
    
    id     = FieldProperty(IAuthnetSubscriptionRead['id'])
    ref_id = FieldProperty(IAuthnetSubscriptionRead['ref_id'])

class IAuthnetSubscriptionCreate(IAuthnetSubscriptionWrite):
    """Represents an ARB Subscription creation request."""
    pass

class SAuthnetSubscriptionCreate(SAuthnetSubscriptionWrite):
    """Reifier for an ARB Subscription creation request object."""
    implements(IAuthnetSubscriptionCreate)

class IAuthnetSubscriptionUpdate(IAuthnetSubscriptionWrite):
    """Represents an ARB Subscription update request."""
    
    id       = TextLine(title=u'Subscription ID',     description=u'The subscription\'s ID.', max_length=13, required=True)
    schedule = Object(title=u'Subscription Schedule', description=u'The billing schedule for the subscription.', schema=ISchedule, required=False)
    amount   = TextLine(title=u'Billing Amount',      description=u'The amount to be billed to the customer for each payment in the subscription.', max_length=15, constraint=CURRENCY.match, required=True)

class SAuthnetSubscriptionUpdate(SAuthnetSubscriptionWrite):
    """Reifier for an ARB Subscription update request object."""
    
    implements(IAuthnetSubscriptionUpdate)
    
    id       = FieldProperty(IAuthnetSubscriptionUpdate['id'])
    schedule = FieldProperty(IAuthnetSubscriptionUpdate['schedule'])
    amount   = FieldProperty(IAuthnetSubscriptionUpdate['amount'])

class IAuthnetSubscriptionStatus(IAuthnetSubscriptionRead):
    """Represents an ARB Subscription status request."""
    pass

class SAuthnetSubscriptionStatus(SAuthnetSubscriptionRead):
    """Reifier for an ARB Subscription status request object."""
    implements(IAuthnetSubscriptionStatus)

class IAuthnetSubscriptionCancel(IAuthnetSubscriptionRead):
    """Represents an ARB Subscription cancellation request."""
    pass

class SAuthnetSubscriptionCancel(SAuthnetSubscriptionRead):
    """Reifier for an ARB Subscription cancellation request object."""
    
    implements(IAuthnetSubscriptionCancel)

