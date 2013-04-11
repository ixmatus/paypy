import urllib2

from lxml                          import etree as ET

from paypy.adapters                import *
from paypy.exceptions.authnet      import CIMException

from paypy.schemas.authnet.cim     import *
from paypy.serializers.authnet.cim import Serialize
from paypy.schemas.authnet.cim     import ICim

from paypy.adapters.authnet.aim    import TransactionResult

PROFILE  = 'CustomerProfileRequest'
PAYMENT  = 'CustomerPaymentProfileRequest'
SHIPPING = 'CustomerShippingAddressRequest'
CIM_REQUEST_ELEMENTS    = {'create'   : ('create%s' % PROFILE,
                                         'create%s' % PAYMENT,
                                         'create%s' % SHIPPING,
                                         'createCustomerProfileTransactionRequest'),
                           'update'   : ('update%s' % PROFILE,
                                         'update%s' % PAYMENT,
                                         'update%s' % SHIPPING,
                                         'updateSplitTenderGroupRequest'),
                           'retrieve' : ('getCustomerProfileIdsRequest',
                                         'get%s' % PROFILE,
                                         'get%s' % PAYMENT,
                                         'get%s' % SHIPPING),
                           'remove'   : ('delete%s' % PROFILE,
                                         'delete%s' % PAYMENT,
                                         'delete%s' % SHIPPING)
                          }

class ProfileResult(Result):
    """Represent a profile result as an object."""
    
    def __init__(self, data):
        """Set the result items."""
        
        ANET_XMLNS = ' xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd"'
        
        raw       = data
        data      = data.replace(ANET_XMLNS, '')
        
        self.root = ET.XML(data)
        messages  = self.root.find('messages')
        
        self.result_code = messages.find('resultCode').text
        self.code        = messages.find('message/code').text
        self.reason      = messages.find('message/text').text
        self.profile_id  = None
        self.raw         = raw
        self.ref_id      = None
        
        profile_id       = self.root.find('customerProfileId')
        
        if profile_id is not None:
            self.profile_id = profile_id.text
        
        self._index = 0
        
        ref_id = self.root.find('refId')
        
        if ref_id:
            self.ref_id = ref_id
    
    def __str__(self):
        """Calling str on the object will return the profile id or response reason."""
        
        return self.reason
    
    def __repr__(self):
        """Object representation of the profile result object."""
        
        return '<%s at 0x%x %s>' % (self.__class__.__name__, abs(id(self)), self.result_code)

class CreateProfileResult(ProfileResult):
    """Represent a profile creation result as an object."""
    
    def __init__(self, data):
        
        super(CreateProfileResult, self).__init__(data)
        
        # Get all ids
        if self.root.tag == 'getCustomerProfileIdsResponse':
            ids = self.root.find('ids')
            
            if ids is not None:
                self.profile_ids = [x.text for x in ids]
            else:
                self.profile_ids = []
        
        # Grab the shipping and payment profile ids
        if self.root.tag == 'createCustomerProfileResponse':
            # Validation element?
            validation_responses = self.root.find('validationDirectResponse')
            
            if validation_responses:
                # Loop through them
                self.validation = [TransactionResult(x.text, ',') for x in validation_responses]
            else:
                self.validation = []
            
            # If there are any payment profile id's, get them
            payment_profiles = self.root.find('customerPaymentProfileIdList')
            
            if payment_profiles:
                self.payment_ids = [x.text for x in payment_profiles]
            else:
                self.payment_ids = []
            
            # If there are any shipping profile id's, get them
            shipping_profiles = self.root.find('customerShippingAddressIdList')
            
            if shipping_profiles:
                self.shipping_ids = [x.text for x in shipping_profiles]
            else:
                self.shipping_ids = []
        
        # Grab the created payment profile id
        if self.root.tag == 'createCustomerPaymentProfileResponse':
            # Validation element?
            validation = self.root.find('validationDirectResponse')
            
            if validation is not None:
                # Loop through them
                self.validation = [TransactionResult(validation.text, ',')]
            else:
                self.validation = []
            
            payment_profile = self.root.find('customerPaymentProfileId')
            
            if payment_profile is not None:
                self.payment_ids = [payment_profile.text]
            else:
                self.payment_ids = []
        
        # Grab the created shipping id
        if self.root.tag == 'createCustomerShippingAddressResponse':
            shipping_profile = self.root.find('customerAddressId')
            
            if shipping_profile is not None:
                self.shipping_ids = [shipping_profile.text]
            else:
                self.shipping_ids = []
        
        # Return a transaction result object
        if self.root.tag == 'createCustomerProfileTransactionResponse':
            transaction = self.root.find('directResponse')
            
            if transaction is not None:
                self.transaction = TransactionResult(transaction.text)
            else:
                self.transaction = None
        
    def __str__(self):
        """Calling str on the object will return the profile id or response reason."""
        
        if self.profile_id:
            return self.profile_id
        
        return self.reason

class UpdateProfileResult(ProfileResult):
    """Represent a profile update result as an object."""
    
    def __init__(self, data):
        
        super(UpdateProfileResult, self).__init__(data)
        
        if self.root.tag == 'updateCustomerPaymentProfileResponse':
            self.validation = None
            validation      = self.root.find('validationDirectResponse')
            
            if validation is not None:
                self.validation = TransactionResult(validation.text, ',')

class ValidatePaymentProfile(ProfileResult):
    """Represent a validation request as a result object."""
    
    def __init__(self, data):
        
        super(UpdateProfileResult, self).__init__(data)
        
        self.validation = None
        validation      = self.root.find('directResponse')
        
        if validation:
            self.validation = TransactionResult(validation.text)

class RetrieveProfileResult(ProfileResult):
    """Represent a profile retrieval result as an object."""
    
    def __init__(self, data):
        
        super(RetrieveProfileResult, self).__init__(data)
        
        self.results = None
        
        # Get all ids
        if self.root.tag == 'getCustomerProfileIdsResponse':
            ids = self.root.find('ids')
            
            if ids is not None:
                self.results = [x.text for x in ids]
            else:
                self.results = []
        
        # Get a profile
        if self.root.tag == 'getCustomerProfileResponse':
            profile        = self.root.find('profile')
            profile_id     = profile.find('customerProfileId').text
            customer_id    = profile.find('merchantCustomerId')
            customer_email = profile.find('email')
            customer_desc  = profile.find('description')
            
            self.results = {'id'       : profile_id,
                            'customer' : {},
                            'billing'  : [],
                            'shipping' : []}
            
            # Get the generic customer fields
            if customer_id is not None:
                self.results['customer']['id'] = customer_id.text
            
            if customer_email is not None:
                self.results['customer']['email'] = customer_email.text
            
            if customer_desc is not None:
                self.results['customer']['description'] = customer_desc.text
            
            payment_profiles  = profile.findall('paymentProfiles')
            shipping_profiles = profile.findall('shipToList')
            
            for payment in payment_profiles:
                self.results['billing'].append(self._billing(payment))
            
            for shipping in shipping_profiles:
                self.results['shipping'].append(self._shipping(shipping))
        
        # Get a customer payment profile
        if self.root.tag == 'getCustomerPaymentProfileResponse':
            self.results = {'billing' : self._billing(self.root.find('paymentProfile'))}
        
        # Get a customer shipping profile
        if self.root.tag == 'getCustomerShippingAddressResponse':
            address = self.root.find('address')
            self.results = {'shipping' : self._shipping(address)}
            
            shipping_id  = address.find('customerAddressId')
            
            if shipping_id is not None:
                self.results['id'] = shipping_id.text
    
    def _billing(self, data):
        """Translate a given XML tree to a dictionary."""
        
        bill_to       = data.find('billTo')
        payment_id    = data.find('customerPaymentProfileId')
        customer_type = data.find('customerType')
        payment       = data.find('payment')
        billing       = {'id' : payment_id.text}
        
        if customer_type is not None:
            billing['type']    = customer_type.text
        
        if bill_to is not None:
            billing['profile'] = self._shipping(bill_to)
        
        if payment is not None:
            billing['payment'] = {}
            
            # Credit card or bank account?
            card = payment.find('creditCard')
            if card is not None:
                number     = card.find('cardNumber')
                expiration = card.find('expirationDate')
                
                billing['payment']['card'] = {'number' : number.text, 'expiration' : expiration.text}
            else:
                bank    = payment.find('bankAccount')
                routing = bank.find('routingNumber')
                account = bank.find('accountNumber')
                
                billing['payment']['bank'] = {'account' : account.text, 'routing' : routing.text}
        
        return billing
        
    def _shipping(self, data):
        """Translate a given XML tree to a dictionary."""
        
        shipping    = {}
        
        firstname = data.find('firstName')
        if firstname is not None:
            shipping['firstname'] = firstname.text
        
        lastname  = data.find('lastName')
        if lastname is not None:
            shipping['lastname'] = lastname.text
        
        company   = data.find('company')
        if company is not None:
            shipping['company'] = company.text
        
        address   = data.find('address')
        if address is not None:
            shipping['address'] = address.text
        
        city      = data.find('city')
        if city is not None:
            shipping['city'] = city.text
        
        state     = data.find('state')
        if state is not None:
            shipping['state'] = state.text
        
        zipcode   = data.find('zip')
        if zipcode is not None:
            shipping['zip'] = zipcode.text
        
        country   = data.find('country')
        if country is not None:
            shipping['country'] = country.text
        
        phone     = data.find('phoneNumber')
        if phone is not None:
            shipping['phone'] = phone.text
        
        fax = data.find('faxNumber')
        if fax is not None:
            shipping['fax'] = fax.text
        
        return shipping
    
    def __len__(self):
        """Return number of items fetched.
        
        This is only really useful for retrieving all profile ID's in
        the system.
        
        """
        
        if hasattr(self, 'profile_ids'):
            return len(self.profile_ids)
        elif self.code == 'I00001': 
            return 1
        else:
            return 0
    
    def __getitem__(self, key):
        """Return an item from a given index."""
        
        if self.root.tag == 'getCustomerProfileIdsResponse':
            if isinstance(key, int):
                return self.results[key]
            else:
                raise TypeError('list indices must be integers, not str')
        elif self.root.tag == 'getCustomerProfileResponse':
            return self.results[key]
        elif self.root.tag == 'getCustomerPaymentProfileResponse':
            return self.results[key]
        elif self.root.tag == 'getCustomerShippingAddressResponse':
            return self.results[key]
    
    def next(self):
        """Produce the next item in the result set."""
        
        if self._index >= len(self.results):
            raise StopIteration
        
        result = self.results[self._index]
        self._index +=1
        
        return result
    
    def __iter__(self):
        """Make the result object iterable."""
        
        return self

class RemoveProfileResult(ProfileResult):
    """Represent a profile removal result as an object."""
    
    def __init__(self, data):
        
        super(RemoveProfileResult, self).__init__(data)

class CustomerProfile(Adapter):
    """Authorize.net CIM (Customer Information Manager) object adapter.
    
    Represent an Authorize.net Customer record and provide methods for
    creating, updating, retrieving, and deleting one.
    
    """
    
    def __init__(self, options):
        
        ENDPOINT_XML_PRODUCTION = 'api.authorize.net/xml/v1/'
        ENDPOINT_XML_TEST       = 'apitest.authorize.net/xml/v1/'
        REQUEST_PATH            = 'request.api'
        
        if not ICim.providedBy(options):
            raise ARBException('the options object must provide a valid schema interface')
        
        self.options    = options
        self.serialized = Serialize(options)
        
        testing = options.profile.testing
        host    = ENDPOINT_XML_TEST if testing else ENDPOINT_XML_PRODUCTION
        
        self.connection                         = urllib2.Request(url='https://' + host + REQUEST_PATH, headers={'Content-Type' : 'text/xml'})
    
    def create(self):
        """Create a CIM record."""
        
        # Be sure we're calling create on the right schema
        if not IAuthnetProfileCreate.providedBy(self.options.profile)         and \
           not IAuthnetProfileCreateBilling.providedBy(self.options.profile)  and \
           not IAuthnetProfileCreateShipping.providedBy(self.options.profile) and \
           not IAuthnetProfileCreateTransaction.providedBy(self.options.profile):
            
            raise CIMException('a creation request must conform to one of the creation interfaces')
        
        return CreateProfileResult(self._request())
    
    def update(self):
        """Update a CIM record."""
        
        if not IAuthnetProfileUpdate.providedBy(self.options.profile)         and \
           not IAuthnetProfileUpdateBilling.providedBy(self.options.profile)  and \
           not IAuthnetProfileUpdateShipping.providedBy(self.options.profile) and \
           not IAuthnetProfileUpdateSplitTender.providedBy(self.options.profile):
            
            raise CIMException('an update request must conform to one of the update interfaces')
        
        return UpdateProfileResult(self._request())
    
    def retrieve(self):
        """Retrieve a CIM record."""
        
        if not IAuthnetProfileRetrieveAll.providedBy(self.options.profile)     and \
           not IAuthnetProfileRetrieve.providedBy(self.options.profile)        and \
           not IAuthnetProfileRetrieveBilling.providedBy(self.options.profile) and \
           not IAuthnetProfileRetrieveShipping.providedBy(self.options.profile):
            
            raise CIMException('a retrieval request must conform to one of the retrieval interfaces')
        
        return RetrieveProfileResult(self._request())
    
    def remove(self):
        """Remove a CIM record."""
        
        if not IAuthnetProfileDelete.providedBy(self.options.profile)        and \
           not IAuthnetProfileDeleteBilling.providedBy(self.options.profile) and \
           not IAuthnetProfileDeleteShipping.providedBy(self.options.profile):
            
            raise CIMException('a removal request must conform to one of the deletion interfaces')
        
        return RemoveProfileResult(self._request())
    
    def _request(self):
        """Send the request to authorize.net."""
        
        data = str(self.serialized)
        
        self.connection.headers['Content-Length'] = str(len(data))
        self.connection.data                      = data
        
        request   = urllib2.urlopen(self.connection)
        result    = request.read()
        
        return result
