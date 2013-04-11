"""Payment API

Provide an isomorphic payment interface for multiple different payment
gateway API's.

"""

from paypy.exceptions.payment import PaymentException

ADAPTERS = ('authnet', 'google', 'paypal')

class Payment(object):
    """Instantiate with a given configuration and make a payment."""
    
    def __init__(self, configuration, adapter='authnet'):
        
        # A adapter must be specified
        if not adapter:
            raise PaymentException('You must specify a gateway adapter')
        
        adapter = adapter.lower()
        
        # Is the driver allowed?
        if adapter not in ADAPTERS:
            raise PaymentException('The configured adapter is not supported')
        
        # Lazy load
        adapter_module = __import__('paypy.adapters.%s' % adapter, fromlist=['paypy.adapters'])
        
        # Instantiate the driver with options
        self.adapter   = adapter_module.Transaction(configuration)
    
    def process(self):
        """Process a payment with the configured driver and options."""
        
        return self.adapter.process()
