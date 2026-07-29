from enum import Enum


class UserRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    TECHNICIAN = "TECHNICIAN"
    CASHIER = "CASHIER"
    SUPPORT = "SUPPORT"