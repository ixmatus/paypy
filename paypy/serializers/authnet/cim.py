from lxml                      import etree as ET
from paypy.schemas.authnet.cim import *
from paypy.schemas.payment     import ICreditCard, IBank

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
                           'delete'   : ('delete%s' % PROFILE,
                                         'delete%s' % PAYMENT,
                                         'delete%s' % SHIPPING)
                          }

class SerializeException(Exception):
    """Serializer exception class."""
    pass

class Serialize(object):
    """Serializer for schema -> xml -> string."""
    
    def __init__(self, schema):
        
        if not isinstance(schema, SCim):
            raise SerializeException('the schema object must be an instance of the SCim schema class')
        
        self.schema = schema
        self.result = self._to_xml(schema)
    
    def _prototype_address(self, parent, schema, tag):
        """A pseudo macro function for producing a billing profile element."""
        
        address = ET.SubElement(parent, tag)
        
        if schema.firstname is not None:
            ET.SubElement(address, 'firstName').text = schema.firstname
        if schema.lastname is not None:
            ET.SubElement(address, 'lastName').text  = schema.lastname
        if schema.company is not None:
            ET.SubElement(address, 'company').text   = schema.company
        if schema.address is not None:
            ET.SubElement(address, 'address').text   = schema.address
        if schema.city is not None:
            ET.SubElement(address, 'city').text      = schema.city
        if schema.state is not None:
            ET.SubElement(address, 'state').text     = schema.state
        if schema.postal_code is not None:
            ET.SubElement(address, 'zip').text       = schema.postal_code
        if schema.country is not None:
            ET.SubElement(address, 'country').text   = schema.country
        if schema.phone is not None:
            ET.SubElement(address, 'phoneNumber').text = schema.phone
        if schema.fax is not None:
            ET.SubElement(address, 'faxNumber').text   = schema.fax
        
        return address
    
    def _prototype_transaction(self, root, parent, transaction, tag):
        """A pseudo macro function for producing a transaction element."""
        
        transact = ET.SubElement(parent, tag)
        tranny   = transaction.transaction
        
        # Build out rest of transaction body
        if tranny.amount is not None:
            ET.SubElement(transact, 'amount').text = tranny.amount
        
        # Taxes! Yay!
        if tranny.tax is not None:
            tax = ET.SubElement(transact, 'tax')
            
            ET.SubElement(tax, 'amount').text      = tranny.tax.amount
            ET.SubElement(tax, 'name').text        = tranny.tax.name
            ET.SubElement(tax, 'description').text = tranny.tax.description
        
        # Shipping...Freight...Authorize.net can't make up their minds!
        if tranny.freight is not None:
            # Note, we use "freight" but authorize.net wants it "shipping"
            freight = ET.SubElement(transact, 'shipping')
            
            ET.SubElement(freight, 'amount').text      = tranny.freight.amount
            ET.SubElement(freight, 'name').text        = tranny.freight.name
            ET.SubElement(freight, 'description').text = tranny.freight.description
        
        # Duty...don't buy it at the airport!
        if tranny.duty is not None:
            duty = ET.SubElement(transact, 'duty')
            
            ET.SubElement(duty, 'amount').text      = tranny.duty.amount
            ET.SubElement(duty, 'name').text        = tranny.duty.name
            ET.SubElement(duty, 'description').text = tranny.duty.description
        
        # We can have multiple line items...
        if tranny.line_item is not None:
            for line_item in tranny.line_item:
                oh_yes = ET.SubElement(transact, 'lineItems')
                
                ET.SubElement(oh_yes, 'itemId').text      = line_item.id
                ET.SubElement(oh_yes, 'name').text        = line_item.name
                ET.SubElement(oh_yes, 'description').text = line_item.description
                ET.SubElement(oh_yes, 'quantity').text    = str(line_item.quantity)
                ET.SubElement(oh_yes, 'unitPrice').text   = line_item.price
                ET.SubElement(oh_yes, 'taxable').text     = str(line_item.taxable).lower()
        
        
        # Profile ID's and transaction ID's
        if transaction.id is not None:
            ET.SubElement(transact, 'customerProfileId').text = str(transaction.id)
        if transaction.billing_id is not None:
            ET.SubElement(transact, 'customerPaymentProfileId').text = str(transaction.billing_id)
        if transaction.shipping_id is not None:
            ET.SubElement(transact, 'customerShippingAddressId').text = str(transaction.shipping_id)
        if tranny.transaction_id is not None:
            ET.SubElement(transact, 'transId').text = tranny.transaction_id
        
        # If we have any data on the user
        order = False
        
        if tranny.invoice is not None:
            order = ET.SubElement(transact, 'order')
            ET.SubElement(order, 'invoiceNumber').text = tranny.invoice
        if tranny.description is not None:
            if not order:
                order = ET.SubElement(transact, 'order')
            ET.SubElement(order, 'description').text = tranny.description
        if tranny.po is not None:
            if not order:
                order = ET.SubElement(transact, 'order')
            ET.SubElement(order, 'purchaseOrderNumber').text = tranny.po
        
        # Tax exemption and miscellany
        if tranny.tax_exempt is not None:
            ET.SubElement(transact, 'taxExempt').text = tranny.tax_exempt
        if tranny.recurring_billing is not None:
            ET.SubElement(transact, 'recurringBilling').text = str(tranny.recurring_billing).upper()
        if tranny.split_tender_id is not None:
            ET.SubElement(transact, 'splitTenderId').text = tranny.split_tender_id
        if tranny.ccv is not None:
            ET.SubElement(transact, 'cardCode').text = tranny.ccv
        
        # Extra options...
        extra_options = []
        
        if tranny.version is not None:
            extra_options.append('x_version=%s' % tranny.version)
        if tranny.delim_char is not None:
            extra_options.append('x_delim_char=%s' % tranny.delim_char)
        if tranny.delim_data is not None:
            extra_options.append('x_delim_data=%s' % tranny.delim_data)
        if tranny.relay_response is not None:
            extra_options.append('x_relay_response=%s' % tranny.relay_response)
        if tranny.customer_id is not None:
            extra_options.append('x_cust_id=%s' % tranny.customer_id)
        if tranny.customer_ip is not None:
            extra_options.append('x_customer_ip=%s' % tranny.customer_ip)
        if tranny.customer_email is not None:
            extra_options.append('x_email_customer=%s' % tranny.customer_email)
        if tranny.email is not None:
            extra_options.append('x_email=%s' % tranny.email)
        if tranny.description is not None:
            extra_options.append('x_description=%s' % tranny.description)
        if tranny.merchant_email is not None:
            extra_options.append('x_merchant_email=%s' % tranny.merchant_email)
        if tranny.allow_partial_auth is not None:
            extra_options.append('x_allow_partial_auth=%s' % tranny.allow_partial_auth)
        if tranny.auth_code is not None:
            extra_options.append('x_auth_code=%s' % tranny.auth_code)
        if tranny.authentication_indicator is not None:
            extra_options.append('x_authentication_indicator=%s' % tranny.authentication_indicator)
        if tranny.cardholder_authentication_value is not None:
            extra_options.append('x_cardholder_authentication_value=%s' % tranny.cardholder_authentication_value)
        if tranny.duplicate_window is not None:
            extra_options.append('x_duplicate_window=%s' % tranny.duplicate_window)
        if tranny.encap_char is not None:
            extra_options.append('x_encap_char=%s' % tranny.encap_char)
        if tranny.footer_email_receipt is not None:
            extra_options.append('x_footer_email_receipt=%s' % tranny.footer_email_receipt)
        if tranny.header_email_receipt is not None:
            extra_options.appen('x_header_email_receipt=%s' % tranny.header_email_receipt)
        if tranny.url is not None:
            extra_options.append('x_url=%s' % tranny.url)
        
        if extra_options is not None:
            extra      = ET.SubElement(root, 'extraOptions')
            extra.text = ET.CDATA('&'.join(extra_options))
    
    def _to_xml(self, schema):
        """Map a schema object to a valid authnet ARB request XML document."""
        
        trans     = schema.profile
        auth      = schema.authentication
        
        if IAuthnetProfileCreate.providedBy(trans):
            operation = 'create' + PROFILE
        elif IAuthnetProfileCreateBilling.providedBy(trans):
            operation = 'create' + PAYMENT
        elif IAuthnetProfileCreateShipping.providedBy(trans):
            operation = 'create' + SHIPPING
        elif IAuthnetProfileCreateTransaction.providedBy(trans):
            operation = 'createCustomerProfileTransactionRequest'
        elif IAuthnetProfileUpdate.providedBy(trans):
            operation = 'update' + PROFILE
        elif IAuthnetProfileUpdateBilling.providedBy(trans):
            operation = 'update' + PAYMENT
        elif IAuthnetProfileUpdateShipping.providedBy(trans):
            operation = 'update' + SHIPPING
        elif IAuthnetProfileUpdateSplitTender.providedBy(trans):
            operation = 'updateSplitTenderGroupRequest'
        elif IAuthnetProfileRetrieveAll.providedBy(trans):
            operation = 'getCustomerProfileIdsRequest'
        elif IAuthnetProfileRetrieve.providedBy(trans):
            operation = 'get' + PROFILE
        elif IAuthnetProfileRetrieveBilling.providedBy(trans):
            operation = 'get' + PAYMENT
        elif IAuthnetProfileRetrieveShipping.providedBy(trans):
            operation = 'get' + SHIPPING
        elif IAuthnetProfileDelete.providedBy(trans):
            operation = 'delete' + PROFILE
        elif IAuthnetProfileDeleteBilling.providedBy(trans):
            operation = 'delete' + PAYMENT
        elif IAuthnetProfileDeleteShipping.providedBy(trans):
            operation = 'delete' + SHIPPING
        elif IAuthnetProfileValidate.providedBy(trans):
            operation = 'validateCustomerPaymentProfileRequest'
        else:
            raise SerializeException('the subscription object provided is not supported')
        
        # Build the document root elementp
        root = ET.Element(operation, xmlns='AnetApi/xml/v1/schema/AnetApiSchema.xsd')
        
        # Merchant authentication element
        authentication = ET.SubElement(root, 'merchantAuthentication')
        ET.SubElement(authentication, 'name').text           = auth.login
        ET.SubElement(authentication, 'transactionKey').text = auth.key
        
        # Set the reference ID
        if hasattr(trans, 'ref_id') and (trans.ref_id is not None):
            ET.SubElement(root, 'refId').text = trans.ref_id
        
        # Now we start having fun - this shit is messay!
        if operation in CIM_REQUEST_ELEMENTS['create']:
            # Creation request
            if IAuthnetProfileCreate.providedBy(trans):
                # Create a brand new customer profile
                profile  = ET.SubElement(root, 'profile')
                
                if trans.customer_id is not None:
                    ET.SubElement(profile, 'merchantCustomerId').text = trans.customer_id
                if trans.description is not None:
                    ET.SubElement(profile, 'description').text = trans.description
                if trans.email is not None:
                    ET.SubElement(profile, 'email').text = trans.email
                
                # Do we have a billing object schema?
                if trans.billing is not None:
                    billing_list = trans.billing
                    
                    # We can have multiple ones...
                    for billing in billing_list:
                        billing_profile = ET.SubElement(profile, 'paymentProfiles')
                        if billing.entity_type is not None:
                            ET.SubElement(billing_profile, 'customerType').text = billing.entity_type
                        # Since a default is specified in the schema, entity type will exist
                        if len(billing.__dict__) > 1:
                            self._prototype_address(billing_profile, billing, 'billTo')
                         
                        if billing.payment is not None:
                            payment_profile = ET.SubElement(billing_profile, 'payment')
                            payment = billing.payment
                            
                            if ICreditCard.providedBy(payment):
                                # Credit card payment type
                                creditcard = ET.SubElement(payment_profile, 'creditCard')
                                ET.SubElement(creditcard, 'cardNumber').text     = payment.number
                                ET.SubElement(creditcard, 'expirationDate').text = payment.expiration.strftime('%Y-%m')
                                if payment.ccv is not None:
                                    ET.SubElement(creditcard, 'cardCode').text   = payment.ccv
                            elif IBank.providedBy(payment):
                                # Bank account payment type
                                bank = ET.SubElement(payment_profile, 'bankAccount')
                                
                                if payment.account_type is not None:
                                    ET.SubElement(bank, 'accountType').text = payment.account_type
                                
                                ET.SubElement(bank, 'routingNumber').text = payment.routing_number
                                ET.SubElement(bank, 'accountNumber').text = payment.account_number
                                ET.SubElement(bank, 'nameOnAccount').text = payment.name_on_account
                                
                                if payment.echeck_type is not None:
                                    ET.SubElement(bank, 'echeckType').text = payment.echeck_type
                                if payment.name is not None:
                                    ET.SubElement(bank, 'bankName').text = payment.name
                            else:
                                raise CIMException('%s is not a supported payment type' % payment.__name__)
                
                if trans.validation is not None:
                    ET.SubElement(root, 'validationMode').text = trans.validation
                    
                if trans.shipping is not None:
                    shipping_list = trans.shipping
                    
                    # We can have multiple ones...
                    for shipping in shipping_list:
                        self._prototype_address(profile, shipping, 'shipToList')
                
            elif IAuthnetProfileCreateBilling.providedBy(trans):
                # Add a new billing profile to a customer profile
                ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                
                payment_profile = ET.SubElement(root, 'paymentProfile')
                
                ET.SubElement(payment_profile, 'customerType').text = trans.billing.entity_type
                
                if trans.billing is not None:
                    self._prototype_address(payment_profile, trans.billing, 'billTo')
                payment = trans.payment
                
                if ICreditCard.providedBy(payment):
                    # Credit card payment type
                    pymnt      = ET.SubElement(payment_profile, 'payment')
                    creditcard = ET.SubElement(pymnt, 'creditCard')
                    ET.SubElement(creditcard, 'cardNumber').text     = payment.number
                    ET.SubElement(creditcard, 'expirationDate').text = payment.expiration.strftime('%Y-%m')
                    if payment.ccv is not None:
                        ET.SubElement(creditcard, 'cardCode').text   = payment.ccv
                elif IBank.providedBy(payment):
                    # Bank account payment type
                    bank = ET.SubElement(payment_profile, 'bankAccount')
                    
                    if payment.account_type is not None:
                        ET.SubElement(bank, 'accountType').text = payment.account_type
                    
                    ET.SubElement(bank, 'routingNumber').text = payment.routing_number
                    ET.SubElement(bank, 'accountNumber').text = payment.account_number
                    ET.SubElement(bank, 'nameOnAccount').text = payment.name_on_account
                    
                    if payment.echeck_type is not None:
                        ET.SubElement(bank, 'echeckType').text = payment.echeck_type
                    if payment.name is not None:
                        ET.SubElement(bank, 'bankName').text = payment.name
                else:
                    raise CIMException('%s is not a supported payment type' % payment.__name__)
            elif IAuthnetProfileCreateTransaction.providedBy(trans):
                # Let's create a transaction!
                type     = trans.transaction.type
                transact = ET.SubElement(root, 'transaction')
                
                if type == 'AUTH_ONLY':
                    self._prototype_transaction(root, transact, trans, 'profileTransAuthOnly')
                elif type == 'AUTH_CAPTURE':
                    self._prototype_transaction(root, transact, trans, 'profileTransAuthCapture')
                elif type == 'CAPTURE_ONLY':
                    self._prototype_transaction(root, transact, trans, 'profileTransCaptureOnly')
                elif type == 'CREDIT':
                    self._prototype_transaction(root, transact, trans, 'profileTransRefund')
                elif type == 'PRIOR_AUTH_CAPTURE':
                    self._prototype_transaction(root, transact, trans, 'profileTransPriorAuthCapture')
                elif type == 'VOID':
                    self._prototype_transaction(root, transact, trans, 'profileTransVoid')
                
            elif IAuthnetProfileCreateShipping.providedBy(trans):
                # Add a new shipping profile to a customer profile
                ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                self._prototype_address(root, trans.shipping, 'address')
        elif operation in CIM_REQUEST_ELEMENTS['update']:
            # Update profile
            if IAuthnetProfileUpdate.providedBy(trans):
                profile = ET.SubElement(root, 'profile')
                
                if trans.customer_id is not None:
                    ET.SubElement(profile, 'merchantCustomerId').text = trans.customer_id
                if trans.description is not None:
                    ET.SubElement(profile, 'description').text = trans.description
                if trans.email is not None:
                    ET.SubElement(profile, 'email').text = trans.email
                
                ET.SubElement(profile, 'customerProfileId').text = str(trans.id)
            
            # Update billing profile
            elif IAuthnetProfileUpdateBilling.providedBy(trans):
                ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                
                payment_profile = ET.SubElement(root, 'paymentProfile')
                
                ET.SubElement(payment_profile, 'customerType').text = trans.billing.entity_type
                
                if trans.billing is not None:
                    self._prototype_address(payment_profile, trans.billing, 'billTo')
                
                payment = trans.payment
                
                if ICreditCard.providedBy(payment):
                    # Credit card payment type
                    pymnt      = ET.SubElement(payment_profile, 'payment')
                    creditcard = ET.SubElement(pymnt, 'creditCard')
                    ET.SubElement(creditcard, 'cardNumber').text     = payment.number
                    ET.SubElement(creditcard, 'expirationDate').text = payment.expiration.strftime('%Y-%m')
                    if payment.ccv is not None:
                        ET.SubElement(creditcard, 'cardCode').text   = payment.ccv
                elif IBank.providedBy(payment):
                    # Bank account payment type
                    bank = ET.SubElement(payment_profile, 'bankAccount')
                    
                    if payment.account_type is not None:
                        ET.SubElement(bank, 'accountType').text = payment.account_type
                    
                    ET.SubElement(bank, 'routingNumber').text = payment.routing_number
                    ET.SubElement(bank, 'accountNumber').text = payment.account_number
                    ET.SubElement(bank, 'nameOnAccount').text = payment.name_on_account
                    
                    if payment.echeck_type is not None:
                        ET.SubElement(bank, 'echeckType').text = payment.echeck_type
                    if payment.name is not None:
                        ET.SubElement(bank, 'bankName').text = payment.name
                
                ET.SubElement(payment_profile, 'customerPaymentProfileId').text = str(trans.billing_id)
                
                if trans.validation is not None:
                    ET.SubElement(root, 'validationMode').text = trans.validation
            
            # Update shipping profile
            elif IAuthnetProfileUpdateShipping.providedBy(trans):
                ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                address = self._prototype_address(root, trans.shipping, 'address')
                
                ET.SubElement(address, 'customerAddressId').text = str(trans.shipping_id)
            
            # Update split tender
            elif IAuthnetProfileUpdateSplitTender.providedBy(trans):
                ET.SubElement(root, 'splitTenderId').text     = str(trans.split_tender_id)
                ET.SubElement(root, 'splitTenderStatus').text = trans.split_tender_status
                
        elif (operation in CIM_REQUEST_ELEMENTS['retrieve']) or (operation in CIM_REQUEST_ELEMENTS['delete']):
            # Retrieval or deletion request
            if operation != 'getCustomerProfileIdsRequest':
                # Get all ID's doesn't need any other elements appended, the others do...
                if IAuthnetProfileRetrieve.providedBy(trans):
                    ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                elif IAuthnetProfileRetrieveBilling.providedBy(trans):
                    ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                    ET.SubElement(root, 'customerPaymentProfileId').text = str(trans.billing_id)
                elif IAuthnetProfileRetrieveShipping.providedBy(trans):
                    ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                    ET.SubElement(root, 'customerAddressId').text = str(trans.shipping_id)
                elif IAuthnetProfileDelete.providedBy(trans):
                    ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                elif IAuthnetProfileDeleteBilling.providedBy(trans):
                    ET.SubElement(root, 'customerProfileId').text        = str(trans.id)
                    ET.SubElement(root, 'customerPaymentProfileId').text = str(trans.billing_id)
                elif IAuthnetProfileDeleteShipping.providedBy(trans):
                    ET.SubElement(root, 'customerProfileId').text = str(trans.id)
                    ET.SubElement(root, 'customerAddressId').text = str(trans.shipping_id)
        
        elif operation == 'validateCustomerPaymentProfileRequest':
            ET.SubElement(root, 'customerProfileId').text        = str(trans.id)
            ET.SubElement(root, 'customerPaymentProfileId').text = str(trans.billing_id)
            
            if trans.shipping_id is not None:
                ET.SubElement(root, 'customerShippingAddressId').text = str(tras.shipping_id)
            if trans.validation is not None:
                ET.SubElement(root, 'validationMode').text = trans.validation
    
        return ET.tostring(root, encoding='UTF-8')
        
    def __str__(self):
        """Return the serialized schema."""
        
        return self.result
    
    def __repr__(self):
        """Return an abbreviated object representation."""
        
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))
