import datetime

from unittest      import TestCase
from paypy.profile import Profile

from paypy.schemas.payment      import SCreditCard, SBank
from paypy.schemas.shipping     import SShipping
from paypy.schemas.billing      import SBilling
from paypy.schemas.authnet      import SMerchantAuthentication, SAuthnetTransaction, STax, SFreight, SLineItem
from paypy.schemas.authnet.cim  import *

class TestCustomerProfile(TestCase):
    """Test the profile library and the different adapters."""
    
    def test_cim(self):
        """Test the authorize.net CIM integration API."""

        auth       = SMerchantAuthentication()
        auth.key   = u'auth_key'
        auth.login = u'auth_login'
        
        cc1            = SCreditCard()
        cc1.number     = u'4111111111111111'
        cc1.expiration = datetime.datetime.strptime('2014-04-01', '%Y-%m-%d')
        
        cc2                 = SBank()
        cc2.name_on_account = u'Richard M Branson'
        cc2.account_number  = u'829330184383'
        cc2.routing_number  = u'122400724'
        cc2.type            = u'checking'
        cc2.name            = u'Bank of America'
        
        # For creation, we have to use a customized billing schema with payment attached to it
        bill1             = SBillingList()
        bill1.firstname   = u'Richard'
        bill1.lastname    = u'Branson'
        bill1.address     = u'8 Navigators Way'
        bill1.city        = u'Podunk'
        bill1.state       = u'California'
        bill1.postal_code = u'92009'
        bill1.country     = u'USA'
        bill1.phone       = u'(383) 993-1392'
        bill1.payment     = cc1
        
        bill2             = SBillingList()
        bill2.firstname   = u'Richard'
        bill2.lastname    = u'Branson'
        bill2.address     = u'91 North Ridge'
        bill2.city        = u'Carlsbad'
        bill2.state       = u'California'
        bill2.postal_code = u'92009'
        bill2.country     = u'USA'
        bill2.phone       = u'(111) 932-1312'
        bill2.payment     = cc2
        
        ship             = SShipping()
        ship.firstname   = u'Richard'
        ship.lastname    = u'Branson'
        ship.address     = u'91 North Ridge'
        ship.city        = u'Carlsbad'
        ship.state       = u'California'
        ship.postal_code = u'92009'
        ship.country     = u'USA'
        ship.phone       = u'(111) 932-1312'
        
        profile             = SAuthnetProfileCreate()
        profile.description = u'A customer profile'
        profile.customer_id = u'24'
        profile.email       = u'starky.4.pspringmeyer@spamgourmet.com'
        profile.billing     = [bill1, bill2]
        profile.shipping    = [ship]
        profile.validation  = u'testMode'
        profile.testing     = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.create()
        
        result_buf = result
        
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print result.reason
        print 'Profile ID: ' + str(result)
        print 'Payment IDs: ' + repr(result.payment_ids)
        print 'Shipping IDs: ' + repr(result.shipping_ids)
        print '------------'
        
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        # Add a payment profile to a given customer profile
        bill             = SBilling()
        bill.firstname   = u'Richard'
        bill.lastname    = u'Branson'
        bill.address     = u'22 Italian Rd.'
        bill.city        = u'Northern Semoia'
        bill.state       = u'California'
        bill.postal_code = u'97873'
        bill.country     = u'USA'
        bill.phone       = u'(383) 993-1392'
        
        cc               = SCreditCard()
        cc.number        = u'4111111111111111'
        cc.expiration    = datetime.datetime.strptime('2018-04-01', '%Y-%m-%d')
        
        profile         = SAuthnetProfileCreateBilling()
        profile.id      = int(str(result_buf))
        profile.billing = bill
        profile.payment = cc
        profile.testing = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.create()
        
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print result
        print 'Payment ID: ' + repr(result.payment_ids)
        print '------------'
        
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        # # And a shipping profile to a given customer profile
        ship             = SShipping()
        ship.firstname   = u'Richard'
        ship.lastname    = u'Branson'
        ship.address     = u'22 Italian Rd.'
        ship.city        = u'Northern Semoia'
        ship.state       = u'California'
        ship.postal_code = u'97873'
        ship.country     = u'USA'
        ship.phone       = u'(383) 993-1392'
        
        profile          = SAuthnetProfileCreateShipping()
        profile.id       = int(str(result_buf))
        profile.shipping = ship
        profile.testing  = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.create()
        
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print result
        print 'Shipping ID: ' + repr(result.shipping_ids)
        print '------------'
        
        # Auth capture
        transaction             = SAuthnetTransaction()
        transaction.amount      = u'200.00'
        transaction.customer_id = u'28'
        transaction.customer_ip = u'127.0.0.1'
        transaction.invoice     = u'29'
        transaction.description = u'This is a transaction description'
        transaction.po          = u'RR9'
        
        tax             = STax()
        tax.name        = u'Tax item name'
        tax.amount      = u'10.00'
        tax.description = u'Tax item description'
        
        freight             = SFreight()
        freight.name        = u'Freight item name'
        freight.amount      = u'4.00'
        freight.description = u'Freight description'
        
        lineitem1             = SLineItem()
        lineitem1.id          = u'SD553'
        lineitem1.name        = u'Red Balloon'
        lineitem1.description = u'Red Balloons with weird stripes'
        lineitem1.quantity    = 5
        lineitem1.price       = u'22.00'
        lineitem1.taxable     = False
        
        lineitem2           = SLineItem()
        lineitem2.id          = u'SD555'
        lineitem2.name        = u'Red Shovel'
        lineitem2.description = u'Red Shovels with weird stripes'
        lineitem2.quantity    = 2
        lineitem2.price       = u'22.00'
        lineitem2.taxable     = False
        
        transaction.tax       = tax
        transaction.freight   = freight
        transaction.line_item = [lineitem1, lineitem2]
        
        trans             = SAuthnetProfileCreateTransaction()
        trans.transaction = transaction
        trans.id          = int(str(result_buf))
        trans.billing_id  = int(result_buf.payment_ids[0])
        trans.shipping_id = int(result_buf.shipping_ids[0])
        trans.testing     = True
        
        cim                = SCim()
        cim.profile        = trans
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.create()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Transaction reason: ' + str(result.transaction)
        print '------------'
        
        # Get all of the profile id
        profile         = SAuthnetProfileRetrieveAll()
        profile.testing = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.retrieve()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        assert len(result) > 0
        
        print 'Profile IDs: ' + repr(result.results)
        print '------------'
        
        # Get a specific profile
        profile         = SAuthnetProfileRetrieve()
        profile.id      = int(str(result_buf))
        profile.testing = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.retrieve()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Customer Profile: ' + repr(result.results)
        print '------------'
        
        # Get a payment profile
        profile            = SAuthnetProfileRetrieveBilling()
        profile.id         = int(str(result_buf))
        profile.billing_id = int(result_buf.payment_ids[0])
        profile.testing    = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.retrieve()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Payment Profile: ' + repr(result.results)
        print '------------'
        
        # Get a shipping profile
        profile             = SAuthnetProfileRetrieveShipping()
        profile.id          = int(str(result_buf))
        profile.shipping_id = int(result_buf.shipping_ids[0])
        profile.testing     = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.retrieve()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Shipping Profile: ' + repr(result.results)
        print '------------'
        
        # Update the profile
        profile             = SAuthnetProfileUpdate()
        profile.id          = int(str(result_buf))
        profile.description = u'Changing the description.'
        profile.email       = u'starky.4.pspringmeyer@spamgourmet.com'
        profile.customer_id = u'24'
        profile.testing     = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.update()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print '------------'
        
        # Update billing
        cc1            = SCreditCard()
        cc1.number     = u'4111111111111111'
        cc1.expiration = datetime.datetime.strptime('2020-04-01', '%Y-%m-%d')
        
        bill1             = SBilling()
        bill1.firstname   = u'Richard'
        bill1.lastname    = u'Branson'
        bill1.address     = u'77 Soaring Eagle'
        bill1.city        = u'Podunk'
        bill1.state       = u'California'
        bill1.postal_code = u'92009'
        bill1.country     = u'USA'
        bill1.phone       = u'(383) 993-1392'
        
        profile              = SAuthnetProfileUpdateBilling()
        profile.id           = int(str(result_buf))
        profile.billing_id   = int(result_buf.payment_ids[0])
        profile.billing      = bill1
        profile.payment      = cc1
        profile.validation   = u'testMode'
        profile.testing     = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.update()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print 'Update Billing Profile: ' + repr(result.validation)
        print '------------'
        
        # Update shipping
        ship             = SShipping()
        ship.firstname   = u'Richard'
        ship.lastname    = u'Branson'
        ship.address     = u'77 Soaring Eagle'
        ship.city        = u'Podunk'
        ship.state       = u'California'
        ship.postal_code = u'92009'
        ship.country     = u'USA'
        ship.phone       = u'(383) 993-1392'
        
        profile              = SAuthnetProfileUpdateShipping()
        profile.id           = int(str(result_buf))
        profile.shipping_id  = int(result_buf.shipping_ids[0])
        profile.shipping     = ship
        profile.testing     = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.update()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        print '------------'
        
        # Remove a payment profile
        profile            = SAuthnetProfileDeleteBilling()
        profile.id         = int(str(result_buf))
        profile.billing_id = int(result_buf.payment_ids[0])
        profile.testing    = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.remove()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        # Remove a shipping profile
        profile             = SAuthnetProfileDeleteShipping()
        profile.id          = int(str(result_buf))
        profile.shipping_id = int(result_buf.shipping_ids[0])
        profile.testing     = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.remove()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
        
        # Remove the whole profile
        profile         = SAuthnetProfileDelete()
        profile.id      = int(str(result_buf))
        profile.testing = True
        
        cim                = SCim()
        cim.profile        = profile
        cim.authentication = auth
        
        profile = Profile(cim)
        result  = profile.remove()
        assert result.code == 'I00001', 'Expected a successful request, received this instead: %s' % result.reason
