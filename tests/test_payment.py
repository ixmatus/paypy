import datetime

from unittest                   import TestCase
from paypy.payment              import Payment
from paypy.schemas.payment      import SCreditCard
from paypy.schemas.billing      import SBilling
from paypy.schemas.authnet      import SAuthnetTransaction
from paypy.schemas.authnet      import SMerchantAuthentication
from paypy.schemas.authnet.aim  import SAim

class TestPayment(TestCase):
    """Test the payment library and the different adapters."""
    
    def test_authnet_aim(self):
        """Test the authorize.net AIM adapter."""
        
        cc            = SCreditCard()
        cc.number     = u'4111111111111111'
        cc.expiration = datetime.datetime.strptime('2014-04-01', '%Y-%m-%d')
        
        billto             = SBilling()
        billto.firstname   = u'Billy'
        billto.lastname    = u'Joel'
        billto.address     = u'48 Notty Road'
        billto.city        = u'Carlsbad'
        billto.state       = u'California'
        billto.postal_code = u'92009'
        billto.country     = u'USA'
        billto.phone       = u'(858) 887-5152'
        
        trans             = SAuthnetTransaction()
        trans.testing     = True
        trans.amount      = u'10.00'
        trans.payment     = cc
        trans.billing     = billto
        trans.customer_id = u'23'
        trans.description = u'Transaction description'
        trans.invoice     = u'423'
        trans.po          = u'S42'
        
        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        aim                = SAim()
        aim.transaction    = trans
        aim.authentication = auth
        
        payment = Payment(aim)
        result  = payment.process()
        assert result.code == 1,           'Expected a succesful transaction, this was returned instead: %s' % str(result)
        assert result.po_number == 'S42', 'Expected "S42" for the purchase order number field'
        assert int(result.customer_id) == 23, 'Expected "10" for the customer id field'
