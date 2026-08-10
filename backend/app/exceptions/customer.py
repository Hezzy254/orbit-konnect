class CustomerNotFoundError(Exception):
    """Raised when a customer cannot be found."""
    pass


class DuplicateCustomerPhoneError(Exception):
    """Raised when a phone number already exists for a company."""
    pass


class DuplicateCustomerEmailError(Exception):
    """Raised when an email already exists for a company."""
    pass