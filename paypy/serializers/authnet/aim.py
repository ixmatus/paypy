import urllib

from paypy.schemas.authnet.aim import SAim

class SerializeException(Exception):
    """Serializer exception class."""
    pass

class Serialize(object):
    """Serializer for schema -> string."""
    
    def __init__(self, schema):
        
        if not isinstance(schema, SAim):
            raise SerializeException('the schema object must be an instance of the SAim schema class')
        
        self.schema = schema
        self.result = self._to_string(schema)
    
    def _to_string(self, schema):
        """Map a schema object to a valid authnet transaction string."""
        
        # We'll make it into a dictionary so we can just urlencode it
        trans          = schema.transaction
        authentication = {'x_login'          : schema.authentication.login, 'x_tran_key' : schema.authentication.key}
        transaction    = {'x_type'           : trans.type,
                          'x_amount'         : trans.amount,
                          'x_version'        : trans.version,
                          'x_method'         : trans.method,
                          'x_delim_char'     : trans.delim_char,
                          'x_delim_data'     : str(trans.delim_data).upper(),
                          'x_url'            : trans.url,
                          'x_relay_response' : str(trans.relay_response).upper(),
                          'x_card_num'       : trans.payment.number,
                          'x_exp_date'       : trans.payment.expiration.strftime('%m/%Y')}
        
        # Create the billing fields
        if trans.billing:
            billto = trans.billing
            
            if billto.firstname:
                transaction['x_first_name'] = urllib.quote(billto.firstname.encode("UTF-8"))
            if billto.lastname:
                transaction['x_last_name']  = urllib.quote(billto.lastname.encode("UTF-8"))
            if billto.company:
                transaction['x_company']    = urllib.quote(billto.company.encode("UTF-8"))
            if billto.address:
                transaction['x_address']    = urllib.quote(billto.address.encode("UTF-8"))
            if billto.city:
                transaction['x_city']       = urllib.quote(billto.city.encode("UTF-8"))
            if billto.state:
                transaction['x_state']      = urllib.quote(billto.state.encode("UTF-8"))
            if billto.postal_code:
                transaction['x_zip']        = billto.postal_code
            if billto.country:
                transaction['x_country']    = urllib.quote(billto.country.encode("UTF-8"))
            if billto.phone:
                transaction['x_phone']      = billto.phone
            if billto.fax:
                transaction['x_fax']        = billto.fax
        
        # Create any shipping fields
        if trans.shipping:
            shipto = trans.shipping
            
            if shipto.firstname:
                transaction['x_ship_to_first_name'] = urllib.quote(shipto.firstname.encode("UTF-8"))
            if shipto.lastname:
                transaction['x_ship_to_last_name']  = urllib.quote(shipto.lastname.encode("UTF-8"))
            if shipto.company:
                transaction['x_ship_to_company']    = urllib.quote(shipto.company.encode("UTF-8"))
            if shipto.address:
                transaction['x_ship_to_address']    = urllib.quote(shipto.address.encode("UTF-8"))
            if shipto.city:
                transaction['x_ship_to_city']       = urllib.quote(shipto.city.encode("UTF-8"))
            if shipto.state:
                transaction['x_ship_to_state']      = urllib.quote(shipto.state.encode("UTF-8"))
            if shipto.postal_code:
                transaction['x_ship_to_zip']        = shipto.postal_code
            if shipto.country:
                transaction['x_ship_to_country']    = urllib.quote(shipto.country.encode("UTF-8"))
            if shipto.phone:
                transaction['x_ship_to_phone']      = shipto.phone
            if shipto.fax:
                transaction['x_ship_to_fax']        = shipto.fax
        
        # Miscellaneous fields
        if trans.payment.ccv:
            transaction['x_card_code']          = trans.payment.ccv
        if trans.customer_id:
            transaction['x_cust_id']            = trans.customer_id
        if trans.customer_ip:
            transaction['x_customer_ip']        = trans.customer_ip
        if trans.customer_email:
            transaction['x_email_customer']     = str(trans.customer_email).upper()
        if trans.email:
            transaction['x_email']              = urllib.quote(trans.email)
        if trans.description:
            transaction['x_description']        = trans.description
        if trans.merchant_email:
            transaction['x_merchant_email']     = trans.merchant_email
        if trans.allow_partial_auth:
            transaction['x_allow_partial_auth'] = trans.allow_partial_auth
        if trans.auth_code:
            transaction['x_auth_code']          = trans.auth_code
        if trans.authentication_indicator:
            transaction['x_authentication_indicator'] = trans.authentication_indicator
        if trans.cardholder_authentication_value:
            transaction['x_cardholder_authentication_value'] = trans.cardholder_authentication_value
        if trans.duplicate_window:
            transaction['x_duplicate_window']     = trans.duplicate_window
        if trans.encap_char:
            transaction['x_encap_char']           = trans.encap_char
        if trans.footer_email_receipt:
            transaction['x_footer_email_receipt'] = trans.footer_email_receipt
        if trans.header_email_receipt:
            transaction['x_header_email_receipt'] = trans.header_email_receipt
        if trans.invoice:
            transaction['x_invoice_num']          = trans.invoice
        if trans.po:
            transaction['x_po_num']               = trans.po
        if trans.split_tender_id:
            transaction['x_split_tender_id']      = trans.split_tender_id
        if trans.tax_exempt:
            transaction['x_tax_exempt']           = str(trans.tax_exempt).upper()
        if trans.recurring_billing:
            transaction['x_recurring_billing']    = str(trans.recurring_billing).upper()
        if trans.test_request:
            transaction['x_test_request']         = str(trans.test_request).upper()
        if trans.transaction_id:
            transaction['x_trans_id']             = trans.transaction_id
        
        transaction.update(authentication)
        encoded = urllib.urlencode(transaction)
        
        # Map the line_item, this is after encoding it because duplicate keys in a dict aren't allowed
        if trans.line_item:
            line_items = []
            for item in trans.line_item:
                items = [item.id, item.name, item.description, item.quantity, item.price, str(item.taxable).upper()]
                line_items.append('<|>'.join([str(x) for x in items]))
            
            if line_items:
                encoded += '&x_line_items=' + '&x_line_items='.join(line_items)
        
        # Map the duty field
        if trans.duty:
            duty     = [trans.duty.name, trans.duty.description, trans.duty.amount]
            encoded += '&x_duty=' + '<|>'.join([str(x) for x in duty])
        
        # Map the tax field
        if trans.tax:
            tax      = [trans.tax.name, trans.tax.description, trans.tax.amount]
            encoded += '&x_tax=' + '<|>'.join([str(x) for x in tax])
        
        # Map the tax field
        if trans.freight:
            freight  = [trans.freight.name, trans.freight.description, trans.freight.amount]
            encoded += '&x_freight=' + '<|>'.join([str(x) for x in freight])
        
        return encoded
        
    
    def __str__(self):
        """Return the serialized schema."""
        
        return self.result
    
    def __repr__(self):
        """Return an abbreviated object representation."""
        
        return '<%s at 0x%x>' % (self.__class__.__name__, abs(id(self)))
