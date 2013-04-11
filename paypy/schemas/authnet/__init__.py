import re
from paypy.schemas.transaction import ITransaction, STransaction
from paypy.schemas.payment     import IPayment
from paypy.schemas.billing     import IBilling
from paypy.schemas.shipping    import IShipping

from zope.interface            import Interface, implements
from zope.schema               import TextLine, Object, Choice, Int, List, Bool
from zope.schema.fieldproperty import FieldProperty

NUMERIC    = re.compile(r'^[0-9]+$')
ALPHA      = re.compile(r'^[\w\-.,\s]+$', re.IGNORECASE | re.UNICODE)
CURRENCY   = re.compile(r'^[0-9]+.[0-9][0-9]$')

# Merchant authentication schema
class IMerchantAuthentication(Interface):
    """Represents an Authorize.net merchant authentication."""
    
    login          = TextLine(title=u'Login ID', description=u'The merchant\'s unique API Login ID', required=True, max_length=20)
    key            = TextLine(title=u'Transaction Key', description=u'The merchant\'s unique Transaction Key', required=True, max_length=16) # tran_key

class SMerchantAuthentication(object):
    """Reifier for an Authorize.net merchant authentication object."""
    
    implements(IMerchantAuthentication)
    
    login = FieldProperty(IMerchantAuthentication['login'])
    key   = FieldProperty(IMerchantAuthentication['key'])
    
    def __repr__(self):
        rep = ''
        
        if self.login:
            rep += self.login + ' '
        if self.key:
            rep += self.key + ' '
        
        return '<%s at 0x%x; %s>' % (self.__class__.__name__, abs(id(self)), rep)

# Sub-transaction schemas
class IItem(Interface):
    amount      = TextLine(title=u'Amount', description=u'Total amount for item', required=False, constraint=CURRENCY.match, max_length=15)
    name        = TextLine(title=u'Name', description=u'Name of item', required=False, max_length=31)
    description = TextLine(title=u'Description', description=u'Description of item', required=False, max_length=255)

class SItem(object):
    implements(IItem)
    
    amount      = FieldProperty(IItem['amount'])
    name        = FieldProperty(IItem['name'])
    description = FieldProperty(IItem['description'])

class ITax(IItem):
    pass
class STax(SItem):
    implements(ITax)
    
    pass

class IDuty(IItem):
    pass
class SDuty(SItem):
    implements(IDuty)
    
    pass

class IFreight(IItem):
    pass
class SFreight(SItem):
    implements(IFreight)
    
    pass

class ILineItem(Interface):
    id   = TextLine(title=u'Item ID', description=u'Line Item ID', required=False, max_length=31)
    name = TextLine(title=u'Name', description=u'Name of item', required=False, max_length=31)
    description = TextLine(title=u'Description', description=u'Description of item', required=False, max_length=255)
    quantity = Int(title=u'Quantity', description=u'Item quantity', required=True)
    price = TextLine(title=u'Unit Price', description=u'Cost of an item per unit excluding tax, freight, and duty.', required=False, constraint=CURRENCY.match, max_length=15)
    taxable = Bool(title=u'Taxable', description=u'Indicates whether the item is subject to tax', required=False, default=False)

class SLineItem(object):
    implements(ILineItem)
    
    id          = FieldProperty(ILineItem['id'])
    name        = FieldProperty(ILineItem['name'])
    description = FieldProperty(ILineItem['description'])
    quantity    = FieldProperty(ILineItem['quantity'])
    price       = FieldProperty(ILineItem['price'])
    taxable     = FieldProperty(ILineItem['taxable'])

# Base transaction schema
class IAuthnetTransaction(ITransaction):
    """Represents an AIM interface."""
    
    # Required fields
    type           = Choice(title=u'Transaction Type', description=u'The type of credit card transaction', values=('AUTH_CAPTURE', 'AUTH_ONLY', 'CAPTURE_ONLY', 'CREDIT', 'PRIOR_AUTH_CAPTURE', 'VOID'), required=True, default='AUTH_CAPTURE')
    amount         = TextLine(title=u'Transaction Amount', description=u'The total amount to be charged or credited including tax, shipping and any other charges', required=False, constraint=CURRENCY.match, max_length=15)
    version        = Choice(title=u'API Version', description=u'Indicates to the system the set of fields that will be included in the response: 3.0 is the default version; 3.1 allows the merchant to utilize partial authorizations and the Card Code feature, and is the current standard version.', values=('3.0', '3.1'), required=True, default='3.1')
    method         = Choice(title=u'Settlement Method', description=u'The method of payment for the transaction, CC (credit card) or ECHECK (electronic check). If left blank, this value will default to CC.', values=('CC', 'ECHECK'), required=True, default='CC')
    delim_char     = Choice(title=u'Delimiter Character', description=u'The character that is used to separate fields in the transaction response. The payment gateway will use the character passed in this field or the value stored in the Merchant Interface if no value is passed.', values=(',', '|', '"', '\'', ':', ';', '/', '\\', '-', '*'), required=True, default='|')
    url            = TextLine(title=u'URL', description=u'URL', required=True, default=u'FALSE')
    delim_data     = Bool(title=u'Delimited Data', description=u'In order to receive a delimited response from the payment gateway, this field must be submitted with a value of TRUE or the merchant has to configure a delimited response through the Merchant Interface.', required=True, default=True)
    relay_response = Bool(title=u'Relay response', description=u'This field, when set to TRUE, instructs the payment gateway to return transaction results to the merchant by means of an HTML form POST to the merchant\'s Web server for a relay response.', required=True, default=False)
    payment        = Object(title=u'Payment', description=u'Payment options', schema=IPayment, required=False)
    
    # Not required fields
    billing        = Object(title=u'Billing Address', description=u'The customer\'s billing address', schema=IBilling,    required=False)
    shipping       = Object(title=u'Shipping Address', description=u'The customer\'s shipping address', schema=IShipping,   required=False)
    
    customer_id                     = TextLine(title=u'Customer ID', description=u'The unique identifier to represent the customer associated with the transaction.', required=False, constraint=ALPHA.match, max_length=20) # cust_id
    customer_ip                     = TextLine(title=u'Customer IP', description=u'The IP address of the customer initiating the transaction. If this value is not passed, it will default to 255.255.255.255.', required=False, constraint=re.compile('^[0-9./]+$').match, max_length=15) # customer_ip
    customer_email                  = Bool(title=u'Customer Email', description=u'Indicates whether an email receipt should be sent to the customer.', required=False)   # email_customer
    email                           = TextLine(title=u'Email', description=u'The email address to which the customer\'s copy of the email receipt is sent when Email Receipts is configured in the Merchant Interface. The email is sent to the customer only if the email address format is valid.', required=False, max_length=255)
    description                     = TextLine(title=u'Description', description=u'The description must be created dynamically on the merchant server or provided on a per- transaction basis. The payment gateway does not perform this function.', required=False, constraint=ALPHA.match, max_length=255)
    
    merchant_email                  = TextLine(title=u'Merchant Email', description=u'Email address to which the merchant\'s copy of the customer confirmation email should be sent. If a value is submitted, an email will be sent to this address as well as the address(es) configured in the Merchant Interface.', required=False, max_length=255)
    
    allow_partial_auth              = Choice(title=u'Allow Partial Authorization', description=u'Set this value if the merchant would like to override a setting in the Merchant Interface', values=('True', 'False', 'T', 'F'), required=False)
    auth_code                       = TextLine(title=u'Authorization Code', description=u'The authorization code for an original transaction not authorized on the payment gateway', required=False, max_length=6)
    authentication_indicator        = TextLine(title=u'Authentication Indicator', description=u'The electronic commerce indicator (ECI) value for a Visa transaction; or the universal cardholder authentication field indicator (UCAF) for a MasterCard transaction obtained by the merchant after the authentication process', required=False)
    cardholder_authentication_value = TextLine(title=u'Cardholder Authentication Value', description=u'The cardholder authentication verification value (CAVV) for a Visa transaction; or accountholder authentication value (AVV)/ universal cardholder authentication field (UCAF) for a MasterCard transaction obtained by the merchant after the authentication process', required=False)
    duplicate_window                = Int(title=u'Duplicate Window', description=u'Indicates in seconds the window of time after a transaction is submitted during which the payment gateway will check for a duplicate transaction. The maximum time allowed is 8 hours (28800 seconds).', min=0, max=28800, required=False)
    encap_char                      = Choice(title=u'Encapsulation Character', description=u'The character that is used to encapsulate the fields in the transaction response. This is only necessary if it is possible that your delimiting character could be included in any field values', values=(',', '|', '"', '\'', ':', ';', '/', '\\', '-', '*'), required=False)
    footer_email_receipt            = TextLine(title=u'This text will appear as the footer on the email receipt sent to the customer.', description=u'', required=False)
    header_email_receipt            = TextLine(title=u'Header Email Receipt', description=u'This text will appear as the header of the email receipt sent to the customer.', required=False)
    
    line_item                       = List(title=u'Line Item', description=u'Itemized order information.', value_type=Object(schema=ILineItem), required=False)
    invoice                         = TextLine(title=u'Invoice ID', description=u'The invoice number must be created dynamically on the merchant server or provided on a per-transaction basis. The payment gateway does not perform this function.', required=False, constraint=ALPHA.match, max_length=20) # invoice_num
    po                              = TextLine(title=u'PO Number', description=u'The purchase order number must be created dynamically on the merchant server or provided on a per-transaction basis. The payment gateway does not perform this function.', required=False, constraint=ALPHA.match, max_length=25) # po_num
    split_tender_id                 = TextLine(title=u'Split Tender ID', description=u'This value is returned in the reply message from the original authorization request.', required=False, constraint=NUMERIC.match)
    duty                            = Object(title=u'Duty', description=u'The duty amount charged OR when submitting this information using the transaction request, delimited duty information including the duty name, description, and amount is also allowed.', schema=IDuty, required=False)
    freight                         = Object(title=u'Freight', description=u'The freight amount charged OR when submitting this information using the transaction request string, delimited freight information including the freight name, description, and amount is also allowed.', schema=IFreight, required=False)
    tax                             = Object(title=u'Tax', description=u'The tax amount charged OR when submitting this information using the transaction request string, delimited tax information including the sales tax name, description, and amount is also allowed.', schema=ITax, required=False)
    tax_exempt                      = Bool(title=u'Tax Exempt', description=u'Indicates whether the transaction is tax exempt.', required=False)
    
    recurring_billing               = Bool(title=u'Recurring Billing', description=u'Indicating marker used by merchant account providers to identify transactions which originate from merchant hosted recurring billing applications. This value is not affiliated with Automated Recurring Billing.', required=False)
    test_request                    = Bool(title=u'Test Request', description=u'Indicates if the transaction should be processed as a test transaction.', required=False)
    transaction_id                  = TextLine(title=u'Transaction ID', description=u'The payment gateway assigned transaction ID of the original transaction.', required=False,  constraint=NUMERIC.match) # trans_id
    ccv                             = TextLine(title=u'Card Code Validation', description=u'Use this only for CIM integration', required=False)
    
class SAuthnetTransaction(STransaction):
    """Reifier of an authnet transaction schema object."""
    
    implements(IAuthnetTransaction)
    
    type                             = FieldProperty(IAuthnetTransaction['type'])
    amount                           = FieldProperty(IAuthnetTransaction['amount'])
    version                          = FieldProperty(IAuthnetTransaction['version'])
    method                           = FieldProperty(IAuthnetTransaction['method'])
    delim_char                       = FieldProperty(IAuthnetTransaction['delim_char'])
    url                              = FieldProperty(IAuthnetTransaction['url'])
    delim_data                       = FieldProperty(IAuthnetTransaction['delim_data'])
    relay_response                   = FieldProperty(IAuthnetTransaction['relay_response'])
    payment                          = FieldProperty(IAuthnetTransaction['payment'])
    billing                          = FieldProperty(IAuthnetTransaction['billing'])
    shipping                         = FieldProperty(IAuthnetTransaction['shipping'])
    customer_id                      = FieldProperty(IAuthnetTransaction['customer_id'])
    customer_ip                      = FieldProperty(IAuthnetTransaction['customer_ip'])
    customer_email                   = FieldProperty(IAuthnetTransaction['customer_email'])
    email                            = FieldProperty(IAuthnetTransaction['email'])
    description                      = FieldProperty(IAuthnetTransaction['description'])
    merchant_email                   = FieldProperty(IAuthnetTransaction['merchant_email'])
    allow_partial_auth               = FieldProperty(IAuthnetTransaction['allow_partial_auth'])
    auth_code                        = FieldProperty(IAuthnetTransaction['auth_code'])
    authentication_indicator         = FieldProperty(IAuthnetTransaction['authentication_indicator'])
    cardholder_authentication_value  = FieldProperty(IAuthnetTransaction['cardholder_authentication_value'])
    duplicate_window                 = FieldProperty(IAuthnetTransaction['duplicate_window'])
    encap_char                       = FieldProperty(IAuthnetTransaction['encap_char'])
    footer_email_receipt             = FieldProperty(IAuthnetTransaction['footer_email_receipt'])
    header_email_receipt             = FieldProperty(IAuthnetTransaction['header_email_receipt'])
    line_item                        = FieldProperty(IAuthnetTransaction['line_item'])
    invoice                          = FieldProperty(IAuthnetTransaction['invoice'])
    po                               = FieldProperty(IAuthnetTransaction['po'])
    split_tender_id                  = FieldProperty(IAuthnetTransaction['split_tender_id'])
    duty                             = FieldProperty(IAuthnetTransaction['duty'])
    freight                          = FieldProperty(IAuthnetTransaction['freight'])
    tax                              = FieldProperty(IAuthnetTransaction['tax'])
    tax_exempt                       = FieldProperty(IAuthnetTransaction['tax_exempt'])
    recurring_billing                = FieldProperty(IAuthnetTransaction['recurring_billing'])
    test_request                     = FieldProperty(IAuthnetTransaction['test_request'])
    transaction_id                   = FieldProperty(IAuthnetTransaction['transaction_id'])
    ccv                              = FieldProperty(IAuthnetTransaction['ccv'])

    def __repr__(self):
        if self.transaction_id:
            rep = self.transaction_id
        elif self.description:
            rep = self.description
        else:
            rep = self.amount
        
        return '<%s at 0x%x; %s>' % (self.__class__.__name__, abs(id(self)), rep)
