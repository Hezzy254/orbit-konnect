class NetworkDeviceNotFoundError(Exception):
    """Raised when a network device cannot be found."""

    pass


class DuplicateNetworkDeviceError(Exception):
    """Raised when a network device already exists for a company."""

    pass


class CrossCompanyNetworkDeviceError(Exception):
    """Raised when a network device belongs to another company."""

    pass


class InvalidNetworkDeviceStatusError(Exception):
    """Raised when an invalid network device state transition is requested."""

    pass


class NetworkDeviceConnectionError(Exception):
    """Raised when a network device connection fails."""

    pass