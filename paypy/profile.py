"""Customer Profile API

Provide an isomorphic interface for managing customer profiles for
multiple different API services.

"""

from paypy.exceptions.profile import ProfileException

ADAPTERS = ('authnet')

class Profile(object):
    """Instantiate with a given configuration and provide profile management methods."""
    
    def __init__(self, configuration, adapter='authnet'):
        
        # A adapter must be specified
        if not adapter:
            raise ProfileException('You must specify a gateway adapter')
        
        adapter = adapter.lower()
        
        # Is the driver allowed?
        if adapter not in ADAPTERS:
            raise ProfileException('The configured adapter is not supported')
        
        # Lazy load
        adapter_module = __import__('paypy.adapters.%s' % adapter, fromlist=['paypy.adapters'])
        
        # Instantiate the driver with options
        self.adapter   = adapter_module.CustomerProfile(configuration)
    
    def create(self):
        """Process a create request."""
        
        return self.adapter.create()
    
    def update(self):
        """Process an update request."""
        
        return self.adapter.update()
    
    def retrieve(self):
        """Process a retrieval request."""
        
        return self.adapter.retrieve()
    
    def remove(self):
        """Process a removal request."""
        
        return self.adapter.remove()
