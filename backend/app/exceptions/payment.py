class PaymentNotFoundError(Exception):
    """Raised when a payment cannot be found."""
    pass


class SubscriptionNotFoundForPaymentError(Exception):
    """Raised when the subscription does not exist for the payment."""
    pass


class CustomerNotFoundForPaymentError(Exception):
    """Raised when the customer does not exist for the payment."""
    pass


class PaymentCustomerMismatchError(Exception):
    """Raised when the payment customer does not match the subscription customer."""
    pass


class CrossCompanyPaymentError(Exception):
    """Raised when payment resources belong to different companies."""
    pass


class InvalidPaymentStatusError(Exception):
    """Raised when an invalid payment state transition is requested."""
    pass


class DuplicatePaymentReferenceError(Exception):
    """Raised when a payment transaction reference already exists."""
    pass
