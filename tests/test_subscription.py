import datetime
import decimal

from unittest           import TestCase
from paypy.subscription import Subscription

from paypy.schemas.payment      import SCreditCard
from paypy.schemas.billing      import SBilling
from paypy.schemas.authnet      import SMerchantAuthentication
from paypy.schemas.authnet.arb  import SArb, SSchedule, SAuthnetSubscriptionCreate, SAuthnetSubscriptionUpdate, SAuthnetSubscriptionStatus, SAuthnetSubscriptionCancel

class TestSubscription(TestCase):
    """Test the profile library and the different adapters."""
    
    def test_authnet_arb(self):
        """Test the authorize.net ARB adapter."""
        
        cc            = SCreditCard()
        cc.number     = u'4111111111111111'
        cc.expiration = datetime.datetime.strptime('2014-04-01', '%Y-%m-%d')
        
        billto             = SBilling()
        billto.firstname   = u'Richard'
        billto.lastname    = u'Branson'
        billto.address     = u'8 Navigators Way'
        billto.city        = u'Podunk'
        billto.state       = u'California'
        billto.postal_code = u'92009'
        billto.country     = u'USA'
        billto.phone       = u'(383) 993-1392'
        
        sub             = SAuthnetSubscriptionCreate()
        sub.testing     = True
        sub.amount      = u'10.00'
        sub.payment     = cc
        sub.billing     = billto
        sub.schedule    = SSchedule()
        sub.customer_id = u'23'
        sub.description = u'Transaction description'
        sub.invoice     = u'423'
        
        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        arb                = SArb()
        arb.subscription   = sub
        arb.authentication = auth

        
        subscription = Subscription(arb)
        result       = subscription.create()
        result_buf   = result
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Subscription ID: %s' % str(result)
        
        # Update
        cc            = SCreditCard()
        cc.number     = u'4111111111111111'
        cc.expiration = datetime.datetime.strptime('2018-04-01', '%Y-%m-%d')
        
        billto             = SBilling()
        billto.address     = u'Crazy Horse Bend'
        billto.city        = u'Encinitas'
        billto.state       = u'California'
        
        sub          = SAuthnetSubscriptionUpdate()
        sub.testing  = True
        sub.id       = unicode(str(result_buf))
        sub.amount   = u'30.00'
        sub.payment  = cc
        
        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        arb                = SArb()
        arb.subscription   = sub
        arb.authentication = auth
        
        subscription = Subscription(arb)
        result       = subscription.update()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Response Code: %s' % str(result)
        
        # Status
        sub         = SAuthnetSubscriptionStatus()
        sub.testing = True
        sub.id      = unicode(str(result_buf))
        
        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        arb                = SArb()
        arb.subscription   = sub
        arb.authentication = auth
        
        subscription = Subscription(arb)
        result       = subscription.status()
        assert result.status, 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Response Code: %s' % str(result)
        
        # Cancel
        sub         = SAuthnetSubscriptionCancel()
        sub.testing = True
        sub.id      = unicode(str(result_buf))
        
        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        arb                = SArb()
        arb.subscription   = sub
        arb.authentication = auth
        
        subscription = Subscription(arb)
        result       = subscription.cancel()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Response Code: %s' % str(result)
    
    def test_authnet_arb_trial(self):
        cc            = SCreditCard()
        cc.number     = u'4111111111111111'
        cc.expiration = datetime.datetime.strptime('2014-04-01', '%Y-%m-%d')
        
        billto             = SBilling()
        billto.firstname   = u'Richard'
        billto.lastname    = u'Branson'
        billto.address     = u'8 Navigators Way'
        billto.city        = u'Podunk'
        billto.state       = u'California'
        billto.postal_code = u'92009'
        billto.country     = u'USA'
        billto.phone       = u'(383) 993-1392'
        
        schedule              = SSchedule()
        schedule.trial_cycles = 1
        
        amount = decimal.Decimal('10.00')
        trial  = str(amount * decimal.Decimal('.5'))
        trial  = trial.split('.')
        
        sub              = SAuthnetSubscriptionCreate()
        sub.testing      = True
        sub.amount       = unicode(amount)
        sub.trial_amount = unicode(trial[0]+'.00')
        sub.payment      = cc
        sub.billing      = billto
        sub.schedule     = schedule
        sub.customer_id  = u'23'
        sub.description  = u'Transaction description'
        sub.invoice      = u'423'
        
        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        arb                = SArb()
        arb.subscription   = sub
        arb.authentication = auth

        
        subscription = Subscription(arb)
        result       = subscription.create()
        result_buf   = result
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        # Cancel
        sub         = SAuthnetSubscriptionCancel()
        sub.testing = True
        sub.id      = unicode(str(result_buf))
        
        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        arb                = SArb()
        arb.subscription   = sub
        arb.authentication = auth
        
        subscription = Subscription(arb)
        result       = subscription.cancel()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
