# Standard fields common to all gateways - individual gateways may have additional fields.
__all__ = ['STANDARD_FIELDS', 'Result', 'Adapter']

STANDARD_FIELDS = ('card_num', 
                   'exp_date',
                   'cvv',
                   'description',
                   'amount',
                   'tax',
                   'shipping',
                   'first_name',
                   'last_name',
                   'company',
                   'address',
                   'city',
                   'state',
                   'zip',
                   'email',
                   'phone',
                   'fax',
                   'ship_to_first_name',
                   'ship_to_last_name',
                   'ship_to_company',
                   'ship_to_address',
                   'ship_to_city',
                   'ship_to_state',
                   'ship_to_zip')

class Result(object):
    """Base result class."""
    
    pass

class Adapter(object):
    """Base adapter class."""
    
    pass
