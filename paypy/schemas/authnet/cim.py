import re

from paypy.schemas             import billing, shipping
from paypy.schemas.payment     import IPayment
from paypy.schemas.authnet     import IMerchantAuthentication
from paypy.schemas.authnet     import IAuthnetTransaction
from zope.interface            import Interface, implements
from zope.schema               import Object, TextLine, Int, Choice, List
from zope.schema.fieldproperty import FieldProperty

ALPHA      = re.compile(r'^[\w\-.,\s]+$', re.IGNORECASE | re.UNICODE)
CURRENCY   = re.compile(r'^[0-9]+.[0-9][0-9]$')

# Custom billing interface to handle lists of billing profiles with payment options attached to them
class IBillingList(billing.IBilling):
    payment = Object(title=u'Payment', description=u'Payment options', schema=IPayment, required=True)
class SBillingList(billing.SBilling):
    implements(IBillingList)
    
    payment = FieldProperty(IBillingList['payment'])

# Parent profile interfaces (for schema validation primarily)
class IAuthnetProfile(Interface):
    pass
class SAuthnetProfile(object):
    implements(IAuthnetProfile)

# Main CIM container
class ICim(Interface):
    """Represents an CIM interface."""
    
    authentication = Object(title=u'Merchant Authentication',   description=u'Represents merchant authentication values.', schema=IMerchantAuthentication, required=True)
    profile        = Object(title=u'Authorize.net CIM', description=u'Represents an authorize.net CIM request', schema=IAuthnetProfile, required=True)
    
class SCim(object):
    """Reifier of an CIM schema object."""
    
    implements(ICim)
    
    authentication = FieldProperty(ICim['authentication'])
    profile        = FieldProperty(ICim['profile'])
    
    def __repr__(self):
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))

# Create profile
class IAuthnetProfileCreate(IAuthnetProfile):
    ref_id       = TextLine(title=u'Reference ID',      description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    description  = TextLine(title=u'Subscription description', description=u'Merchant assigned description of the subscription.', max_length=255, constraint=ALPHA.match, required=False)
    customer_id  = TextLine(title=u'Customer ID', description=u'Merchant-assigned identifier for the customer.', max_length=20, required=False)
    email        = TextLine(title=u'Customer\'s Email', description=u'The customer\'s email address.', max_length=255, required=False)
    billing      = List(title=u'Billing Profile Object List', description=u'List of billing objects.', required=False, value_type=Object(title=u'Billing Address', description=u'The customer\'s billing address', schema=IBillingList))
    shipping     = List(title=u'Shipping Profile Object List', description=u'List of shipping objects', required=False, value_type=Object(title=u'Shipping Address', description=u'The customer\'s shipping address', schema=shipping.IShipping))
    validation   = Choice(title=u'Validation Mode', description=u'Indicates the processing mode for the request.', values=('none', 'testMode', 'liveMode', 'oldLiveMode'), required=False)

class SAuthnetProfileCreate(SAuthnetProfile):
    implements(IAuthnetProfileCreate)
    
    ref_id       = FieldProperty(IAuthnetProfileCreate['ref_id'])
    description  = FieldProperty(IAuthnetProfileCreate['description'])
    customer_id  = FieldProperty(IAuthnetProfileCreate['customer_id'])
    email        = FieldProperty(IAuthnetProfileCreate['email'])
    billing      = FieldProperty(IAuthnetProfileCreate['billing'])
    shipping     = FieldProperty(IAuthnetProfileCreate['shipping'])
    validation   = FieldProperty(IAuthnetProfileCreate['validation'])

# Create billing
class IAuthnetProfileCreateBilling(IAuthnetProfile):
    ref_id  = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    billing = Object(title=u'Billing Address', description=u'The customer\'s billing address', schema=billing.IBilling, required=False)
    payment = Object(title=u'Payment', description=u'Payment options', schema=IPayment, required=True)
    id      = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)

class SAuthnetProfileCreateBilling(SAuthnetProfile):
    implements(IAuthnetProfileCreateBilling)
    
    ref_id  = FieldProperty(IAuthnetProfileCreateBilling['ref_id'])
    billing = FieldProperty(IAuthnetProfileCreateBilling['billing'])
    payment = FieldProperty(IAuthnetProfileCreateBilling['payment'])
    id      = FieldProperty(IAuthnetProfileCreateBilling['id'])

# Create shipping
class IAuthnetProfileCreateShipping(IAuthnetProfile):
    ref_id   = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    shipping = Object(title=u'Shipping Address', description=u'The customer\'s shipping address', schema=shipping.IShipping, required=True)
    id       = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    
class SAuthnetProfileCreateShipping(SAuthnetProfile):
    implements(IAuthnetProfileCreateShipping)
    
    ref_id   = FieldProperty(IAuthnetProfileCreateShipping['ref_id'])
    shipping = FieldProperty(IAuthnetProfileCreateShipping['shipping'])
    id       = FieldProperty(IAuthnetProfileCreateShipping['id'])

# Create transaction
class IAuthnetProfileCreateTransaction(IAuthnetProfile):
    ref_id      = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    transaction = Object(title=u'Transaction Object', description=u'A transaction object', schema=IAuthnetTransaction, required=True)
    id          = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    billing_id  = Int(title=u'Payment Profile ID', description=u'Payment gateway assigned ID associated with the customer payment profile.', required=True)
    shipping_id = Int(title=u'Shipping Profile ID', description=u'Payment gateway assigned ID associated with the customer shipping address.', required=False)

class SAuthnetProfileCreateTransaction(SAuthnetProfile):
    implements(IAuthnetProfileCreateTransaction)
    
    ref_id      = FieldProperty(IAuthnetProfileCreateTransaction['ref_id'])
    transaction = FieldProperty(IAuthnetProfileCreateTransaction['transaction'])
    id          = FieldProperty(IAuthnetProfileCreateTransaction['id'])
    billing_id  = FieldProperty(IAuthnetProfileCreateTransaction['billing_id'])
    shipping_id = FieldProperty(IAuthnetProfileCreateTransaction['shipping_id'])

# Update profile
class IAuthnetProfileUpdate(IAuthnetProfile):
    ref_id      = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    customer_id = TextLine(title=u'Customer ID', description=u'Merchant-assigned identifier for the customer.', max_length=20, required=False)
    description = TextLine(title=u'Subscription description', description=u'Merchant assigned description of the subscription.', max_length=255, constraint=ALPHA.match, required=False)
    email       = TextLine(title=u'Customer\'s Email', description=u'The customer\'s email address.', max_length=255, required=False)
    id          = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    
class SAuthnetProfileUpdate(SAuthnetProfile):
    implements(IAuthnetProfileUpdate)
    
    ref_id      = FieldProperty(IAuthnetProfileUpdate['ref_id'])
    customer_id = FieldProperty(IAuthnetProfileUpdate['customer_id'])
    description = FieldProperty(IAuthnetProfileUpdate['description'])
    email       = FieldProperty(IAuthnetProfileUpdate['email'])
    id          = FieldProperty(IAuthnetProfileUpdate['id'])

# Update billing
class IAuthnetProfileUpdateBilling(IAuthnetProfile):
    ref_id      = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    id          = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    billing_id  = Int(title=u'Payment Profile ID', description=u'Payment gateway assigned ID associated with the customer payment profile.', required=True)
    billing     = Object(title=u'Billing Address', description=u'The customer\'s billing address', schema=billing.IBilling, required=False)
    payment     = Object(title=u'Payment', description=u'Payment options', schema=IPayment, required=True)
    validation  = Choice(title=u'Validation Mode', description=u'Indicates the processing mode for the request.', values=('none', 'testMode', 'liveMode', 'oldLiveMode'), required=False)
    
class SAuthnetProfileUpdateBilling(SAuthnetProfile):
    implements(IAuthnetProfileUpdateBilling)
    
    ref_id      = FieldProperty(IAuthnetProfileUpdateBilling['ref_id'])
    id          = FieldProperty(IAuthnetProfileUpdateBilling['id'])
    billing_id  = FieldProperty(IAuthnetProfileUpdateBilling['billing_id'])
    billing     = FieldProperty(IAuthnetProfileUpdateBilling['billing'])
    payment     = FieldProperty(IAuthnetProfileUpdateBilling['payment'])
    validation  = FieldProperty(IAuthnetProfileUpdateBilling['validation'])

# Update shipping
class IAuthnetProfileUpdateShipping(IAuthnetProfile):
    ref_id      = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    id          = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    shipping_id = Int(title=u'Shipping Profile ID', description=u'Payment gateway assigned ID associated with the customer shipping profile.', required=True)
    shipping    = Object(title=u'Shipping Address', description=u'The customer\'s shipping address', schema=shipping.IShipping, required=False)

class SAuthnetProfileUpdateShipping(SAuthnetProfile):
    implements(IAuthnetProfileUpdateShipping)

    ref_id      = FieldProperty(IAuthnetProfileUpdateShipping['ref_id'])
    id          = FieldProperty(IAuthnetProfileUpdateShipping['id'])
    shipping_id = FieldProperty(IAuthnetProfileUpdateShipping['shipping_id'])
    shipping    = FieldProperty(IAuthnetProfileUpdateShipping['shipping'])

# Update split tender
class IAuthnetProfileUpdateSplitTender(IAuthnetProfile):
    split_tender_id     = Int(title=u'Split Tender ID', description=u'Payment gateway- assigned number associated with the order.', required=True)
    split_tender_status = Choice(title=u'Split Tender Status', description=u'Indicates the status of all transactions associated with the order.', values=('voided', 'completed'), required=True)

class SAuthnetProfileUpdateSplitTender(SAuthnetProfile):
    implements(IAuthnetProfileUpdateSplitTender)
    
    split_tender_id     = FieldProperty(IAuthnetProfileUpdateSplitTender['split_tender_id'])
    split_tender_status = FieldProperty(IAuthnetProfileUpdateSplitTender['split_tender_status'])

# Retrieve all profiles
class IAuthnetProfileRetrieveAll(IAuthnetProfile):
    pass

class SAuthnetProfileRetrieveAll(SAuthnetProfile):
    implements(IAuthnetProfileRetrieveAll)

# Retrieve profile
class IAuthnetProfileRetrieve(IAuthnetProfile):
    id = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)

class SAuthnetProfileRetrieve(SAuthnetProfile):
    implements(IAuthnetProfileRetrieve)
    
    id = FieldProperty(IAuthnetProfileRetrieve['id'])

# Retrieve billing
class IAuthnetProfileRetrieveBilling(IAuthnetProfile):
    id         = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    billing_id = Int(title=u'Payment Profile ID', description=u'Payment gateway assigned ID associated with the customer payment profile.', required=True)

class SAuthnetProfileRetrieveBilling(SAuthnetProfile):
    implements(IAuthnetProfileRetrieveBilling)
    
    id         = FieldProperty(IAuthnetProfileRetrieveBilling['id'])
    billing_id = FieldProperty(IAuthnetProfileRetrieveBilling['billing_id'])

# Retrieve shipping
class IAuthnetProfileRetrieveShipping(IAuthnetProfile):
    id          = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    shipping_id = Int(title=u'Shipping Profile ID', description=u'Payment gateway assigned ID associated with the customer shipping profile.', required=True)

class SAuthnetProfileRetrieveShipping(SAuthnetProfile):
    implements(IAuthnetProfileRetrieveShipping)
    
    id          = FieldProperty(IAuthnetProfileRetrieveShipping['id'])
    shipping_id = FieldProperty(IAuthnetProfileRetrieveShipping['shipping_id'])

# Delete profile
class IAuthnetProfileDelete(IAuthnetProfile):
    id     = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    ref_id = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)

class SAuthnetProfileDelete(SAuthnetProfile):
    implements(IAuthnetProfileDelete)
    
    id     = FieldProperty(IAuthnetProfileDelete['id'])
    ref_id = FieldProperty(IAuthnetProfileDelete['ref_id'])

# Delete billing
class IAuthnetProfileDeleteBilling(IAuthnetProfile):
    ref_id     = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    id         = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    billing_id = Int(title=u'Payment Profile ID', description=u'Payment gateway assigned ID associated with the customer payment profile.', required=True)

class SAuthnetProfileDeleteBilling(SAuthnetProfile):
    implements(IAuthnetProfileDeleteBilling)
    
    id         = FieldProperty(IAuthnetProfileDeleteBilling['id'])
    ref_id     = FieldProperty(IAuthnetProfileDeleteBilling['ref_id'])
    billing_id = FieldProperty(IAuthnetProfileDeleteBilling['billing_id'])

# Delete shipping
class IAuthnetProfileDeleteShipping(IAuthnetProfile):
    ref_id     = TextLine(title=u'Reference ID', description=u'If included in the request, this value will be included in the response. This feature might be especially useful for multi- threaded applications.', max_length=20, required=False)
    id         = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    shipping_id = Int(title=u'Shipping Profile ID', description=u'Payment gateway assigned ID associated with the customer shipping profile.', required=True)

class SAuthnetProfileDeleteShipping(SAuthnetProfile):
    implements(IAuthnetProfileDeleteShipping)
    
    id          = FieldProperty(IAuthnetProfileDeleteShipping['id'])
    ref_id      = FieldProperty(IAuthnetProfileDeleteShipping['ref_id'])
    shipping_id = FieldProperty(IAuthnetProfileDeleteShipping['shipping_id'])

# Validate request schemas
class IAuthnetProfileValidate(IAuthnetProfile):
    id          = Int(title=u'Profile ID', description=u'Payment gateway assigned ID associated with the customer profile.', required=True)
    billing_id  = Int(title=u'Payment Profile ID', description=u'Payment gateway assigned ID associated with the customer payment profile.', required=True)
    shipping_id = Int(title=u'Shipping Profile ID', description=u'Payment gateway assigned ID associated with the customer shipping profile.', required=False)
    card_code   = Int(title=u'CCV Code', description=u'The three- or four-digit number on the back of a credit card (on the front for American Express).', min=999, max=9999, required=False)
    validation  = Choice(title=u'Validation Mode', description=u'Indicates the processing mode for the request.', values=('testMode', 'liveMode'), required=True)
    
class SAuthnetProfileValidate(SAuthnetProfile):
    implements(IAuthnetProfileValidate)
    
    id          = FieldProperty(IAuthnetProfileValidate['id'])
    billing_id  = FieldProperty(IAuthnetProfileValidate['billing_id'])
    shipping_id = FieldProperty(IAuthnetProfileValidate['shipping_id'])
    card_code   = FieldProperty(IAuthnetProfileValidate['card_code'])
    validation  = FieldProperty(IAuthnetProfileValidate['validation'])
