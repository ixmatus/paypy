"""Subscription API

Provide an isomorphic subscription interface for multiple different
recurring payment gateway API's.

"""

from paypy.exceptions.subscription import SubscriptionException

ADAPTERS = ('authnet')

class Subscription(object):
    """Instantiate with a given configuration."""
    
    def __init__(self, configuration, adapter='authnet'):
        
        # A adapter must be specified
        if not adapter:
            raise SubscriptionException('You must specify a gateway adapter')
        
        adapter = adapter.lower()
        
        # Is the driver allowed?
        if adapter not in ADAPTERS:
            raise SubscriptionException('The configured adapter is not supported')
        
        # Lazy load
        adapter_module = __import__('paypy.adapters.%s' % adapter, fromlist=['paypy.adapters'])
        
        # Instantiate the driver with options
        self.adapter   = adapter_module.RecurringTransaction(configuration)
    
    def create(self):
        """Submit a subscription with the configured driver and options."""
        
        return self.adapter.create()
    
    def update(self):
        """Update a given subscription with the configured driver and options."""
        
        return self.adapter.update()
    
    def status(self):
        """Retrieve the status of a subscription."""
        
        return self.adapter.status()
    
    def cancel(self):
        """Cancel a given subscription."""
        
        return self.adapter.cancel()
