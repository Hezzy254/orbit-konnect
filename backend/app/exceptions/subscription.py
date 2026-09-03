class SubscriptionNotFoundError(Exception):
    """Raised when a subscription cannot be found."""

    pass


class InvalidSubscriptionStatusError(Exception):
    """Raised when an invalid subscription state transition is requested."""

    pass


class CustomerNotFoundForSubscriptionError(Exception):
    """Raised when the customer does not exist for the subscription."""

    pass


class PackageNotFoundForSubscriptionError(Exception):
    """Raised when the package does not exist for the subscription."""

    pass


class InactiveCustomerError(Exception):
    """Raised when an inactive customer attempts to receive a subscription."""

    pass


class InactivePackageError(Exception):
    """Raised when an inactive package is used for a new subscription."""

    pass


class CrossCompanySubscriptionError(Exception):
    """Raised when subscription resources belong to different companies."""

    pass