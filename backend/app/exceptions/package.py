class PackageNotFoundError(Exception):
    """Raised when a package cannot be found."""

    pass


class DuplicatePackageNameError(Exception):
    """Raised when a package name already exists for a company."""

    pass