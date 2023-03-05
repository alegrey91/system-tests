import inspect
from .structures import PaymentConfiguration


# plan names and their price per unit in cents.
# the name is an internal identifier which is assigned to a stripe priceId object. 
# The price is the price in cents as defined in Stripe price object.
EXPECTED_PRICES = [{"name":"MonthlyPriceID","price":2900},{"name":"YearlyPriceID","price":27600}]


class PaymentTests(object):
    '''
    NOTE: 
    1. In order to implement further tests, it is required to implement the ability to create a new tenant on the backend (frontEgg).
    2. Tests depends on launching the stripe new backend APIs.
    3. User tested must have a valid stripe customer with a valid test CC. The stripeCustomerID need to be defined in activeSubscripiton.StripeCustomerID. Example fo such a stripe test customer id is "cus_NT8XoDsp5Alqwc"
    '''
    
    @staticmethod
    def create_subscription():
        from tests_scripts.payments.subscription import Create
        return PaymentConfiguration(
            name=inspect.currentframe().f_code.co_name,
            test_obj=Create,
            expected_prices = EXPECTED_PRICES
        )      

    @staticmethod
    def cancel_subscription():
        from tests_scripts.payments.subscription import Cancel
        return PaymentConfiguration(
            name=inspect.currentframe().f_code.co_name,
            test_obj=Cancel,
            expected_prices = EXPECTED_PRICES
        )    

    @staticmethod
    def renew_subscription():
        from tests_scripts.payments.subscription import Renew
        return PaymentConfiguration(
            name=inspect.currentframe().f_code.co_name,
            test_obj=Renew,
            expected_prices = EXPECTED_PRICES

        )    

    @staticmethod
    def stripe_checkout():
        from tests_scripts.payments.subscription import Checkout
        return PaymentConfiguration(
            name=inspect.currentframe().f_code.co_name,
            test_obj=Checkout,
            expected_prices = EXPECTED_PRICES

        )   

    @staticmethod
    def stripe_billing_portal():
        from tests_scripts.payments.portal import Portal
        return PaymentConfiguration(
            name=inspect.currentframe().f_code.co_name,
            test_obj=Portal

        )          

    @staticmethod
    def stripe_plans():
        from tests_scripts.payments.plans import Plans
        return PaymentConfiguration(
            name=inspect.currentframe().f_code.co_name,
            test_obj=Plans,
            expected_prices = EXPECTED_PRICES
        )    

