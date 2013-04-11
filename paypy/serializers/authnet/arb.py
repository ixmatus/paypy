from lxml                      import etree as ET
from paypy.schemas.authnet.arb import SArb, IAuthnetSubscriptionCreate, IAuthnetSubscriptionUpdate, IAuthnetSubscriptionStatus, IAuthnetSubscriptionCancel
from paypy.schemas.payment     import ICreditCard, IBank

ARB_REQUEST_ELEMENTS    = {'create' : 'ARBCreateSubscriptionRequest',
                           'update' : 'ARBUpdateSubscriptionRequest',
                           'status' : 'ARBGetSubscriptionStatusRequest',
                           'cancel' : 'ARBCancelSubscriptionRequest'}

class SerializeException(Exception):
    """Serializer exception class."""
    pass

class Serialize(object):
    """Serializer for schema -> xml -> string."""
    
    def __init__(self, schema):
        
        if not isinstance(schema, SArb):
            raise SerializeException('the schema object must be an instance of the SArb schema class')
        
        self.schema = schema
        self.result = self._to_xml(schema)
    
    def _prototype_address(self, parent, schema, tag):
        """A pseudo macro function for producing a billing profile element."""
        
        address = ET.SubElement(parent, tag)
        
        if schema.firstname:
            ET.SubElement(address, 'firstName').text = schema.firstname
        if schema.lastname:
            ET.SubElement(address, 'lastName').text  = schema.lastname
        if schema.company:
            ET.SubElement(address, 'company').text   = schema.company
        if schema.address:
            ET.SubElement(address, 'address').text   = schema.address
        if schema.city:
            ET.SubElement(address, 'city').text      = schema.city
        if schema.state:
            ET.SubElement(address, 'state').text     = schema.state
        if schema.postal_code:
            ET.SubElement(address, 'zip').text       = schema.postal_code
        if schema.country:
            ET.SubElement(address, 'country').text   = schema.country
        
        return address
    
    def _to_xml(self, schema):
        """Map a schema object to a valid authnet ARB request XML document."""
        
        trans     = schema.subscription
        auth      = schema.authentication
        
        if IAuthnetSubscriptionCreate.providedBy(trans):
            operation = ARB_REQUEST_ELEMENTS['create']
        elif IAuthnetSubscriptionUpdate.providedBy(trans):
            operation = ARB_REQUEST_ELEMENTS['update']
        elif IAuthnetSubscriptionStatus.providedBy(trans):
            operation = ARB_REQUEST_ELEMENTS['status']
        elif IAuthnetSubscriptionCancel.providedBy(trans):
            operation = ARB_REQUEST_ELEMENTS['cancel']
        else:
            raise SerializeException('the subscription object provided is not supported')
        
        # Build the document root elementp
        root = ET.Element(operation, xmlns='AnetApi/xml/v1/schema/AnetApiSchema.xsd')
        
        # Merchant authentication element
        authentication = ET.SubElement(root, 'merchantAuthentication')
        ET.SubElement(authentication, 'name').text           = auth.login
        ET.SubElement(authentication, 'transactionKey').text = auth.key
        
        # Set the reference ID
        if trans.ref_id is not None:
            ET.SubElement(root, 'refId').text = trans.ref_id
        
        # Do we have a subscription ID provided?
        if hasattr(trans, 'id'):
            ET.SubElement(root, 'subscriptionId').text = str(trans.id)
        
        # If we are running anything but a Cancel or Status operation, we need to fill out the request
        if operation not in ('ARBCancelSubscriptionRequest', 'ARBGetSubscriptionStatusRequest'):
            subscription = ET.SubElement(root, 'subscription')
            
            # Do we have a name for this subscription?
            if trans.name is not None:
                ET.SubElement(subscription, 'name').text = trans.name
            
            # Build the schedule element
            if trans.schedule is not None:
                sched    = trans.schedule
                
                schedule = ET.SubElement(subscription, 'paymentSchedule')
                interval = ET.SubElement(schedule, 'interval')
                
                ET.SubElement(interval, 'length').text    = str(sched.length)
                ET.SubElement(interval, 'unit').text      = sched.unit
                ET.SubElement(schedule, 'startDate').text = sched.start.strftime('%Y-%m-%d')
                
                ET.SubElement(schedule, 'totalOccurrences').text = str(sched.cycles)
                
                # If a trial, build the element
                if sched.trial_cycles is not None:
                    sched.cycles + sched.trial_cycles
                    ET.SubElement(schedule, 'trialOccurrences').text = str(sched.trial_cycles)
                
            # Build the charge amount element
            if trans.amount is not None:
                ET.SubElement(subscription, 'amount').text = trans.amount
                
            # Build the trial amount
            if trans.trial_amount is not None:
                ET.SubElement(subscription, 'trialAmount').text = trans.trial_amount
                
            # Build the payment element
            if trans.payment is not None:
                if ICreditCard.providedBy(trans.payment):
                    payment = ET.SubElement(subscription, 'payment')
                    credit  = ET.SubElement(payment, 'creditCard')
                    
                    ET.SubElement(credit, 'cardNumber').text     = trans.payment.number
                    ET.SubElement(credit, 'expirationDate').text = trans.payment.expiration.strftime('%Y-%m')
                    
                    if trans.payment.ccv is not None:
                        ET.SubElement(credit, 'cardCode').text = trans.payment.code
                    
                elif IBank.providedBy(trans.payment):
                    payment = ET.SubElement(subscription, 'payment')
                    account = ET.SubElement(subscription, 'bankAccount')
                    
                    ET.SubElement(account, 'accountType').text   = trans.payment.account_type
                    ET.SubElement(account, 'routingNumber').text = trans.payment.routing_number
                    ET.SubElement(account, 'accountNumber').text = trans.payment.account_number
                    ET.SubElement(account, 'nameOnAccount').text = trans.payment.name_on_account
                    ET.SubElement(account, 'echeckType').text    = trans.payment.echeck_type
                    ET.SubElement(account, 'bankName').text      = trans.payment.name
            
            # Build any special order information
            order = False
            
            if trans.invoice is not None:
                order = ET.SubElement(subscription, 'order')
                ET.SubElement(order, 'invoiceNumber').text = trans.invoice
            
            if trans.description is not None:
                if order is False:
                    order = ET.SubElement(subscription, 'order')
                
                ET.SubElement(order, 'description').text   = trans.description

            # Build the customer and bill to elements
            customer = False
            
            if trans.customer_id is not None:
                customer = ET.SubElement(subscription, 'customer')
                ET.SubElement(customer, 'id').text  = trans.customer_id
            if trans.email is not None:
                if customer is False:
                    customer = ET.SubElement(subscription, 'customer')
                
                ET.SubElement(customer, 'email').text = trans.email
            if (trans.billing is not None) and (trans.billing.phone is not None):
                if customer is False:
                    customer = ET.SubElement(subscription, 'customer')
                ET.SubElement(customer, 'phoneNumber').text = trans.billing.phone
            if (trans.billing is not None) and (trans.billing.fax is not None):
                if customer is False:
                    customer = ET.SubElement(subscription, 'customer')
                ET.SubElement(customer, 'faxNumber').text = trans.billing.fax
            
            # Build the billing elements
            if trans.billing is not None:
                self._prototype_address(subscription, trans.billing, 'billTo')
            
            # Build the shipping elements
            if trans.shipping is not None:
                self._prototype_address(subscription, trans.shipping, 'shipTo')
        
        return ET.tostring(root, encoding='UTF-8')
    
    def __str__(self):
        """Return the serialized schema."""
        
        return self.result
    
    def __repr__(self):
        """Return an abbreviated object representation."""
        
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))
