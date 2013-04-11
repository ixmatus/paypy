from zope.interface            import Interface, implements
from zope.schema               import Bool
from zope.schema.fieldproperty import FieldProperty

class ITransaction(Interface):
    """Represents a transaction interface."""
    
    testing = Bool(title=u'Testing', description=u'Is the transaction in test mode?', required=True, default=False)

class STransaction(object):
    """Reifier for a transaction schema object."""
    
    implements(ITransaction)
    testing = FieldProperty(ITransaction['testing'])
