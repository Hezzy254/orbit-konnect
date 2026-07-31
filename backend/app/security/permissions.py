from fastapi import Depends, HTTPException, status

from backend.app.dependencies.auth import get_current_user
from backend.app.models.roles import UserRole
from backend.app.models.user import User


def require_role(*allowed_roles: UserRole):
    """
    Factory that creates role-based authorization dependencies.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker


# ===== Owner =====

require_owner = require_role(
    UserRole.OWNER,
)


# ===== Admin =====

require_admin = require_role(
    UserRole.OWNER,
    UserRole.ADMIN,
)


# ===== Manager =====

require_manager = require_role(
    UserRole.OWNER,
    UserRole.ADMIN,
    UserRole.MANAGER,
)


# ===== Technician =====

require_technician = require_role(
    UserRole.OWNER,
    UserRole.ADMIN,
    UserRole.TECHNICIAN,
)


# ===== Support =====

require_support = require_role(
    UserRole.OWNER,
    UserRole.ADMIN,
    UserRole.SUPPORT,
)


# ===== Cashier =====

require_cashier = require_role(
    UserRole.OWNER,
    UserRole.ADMIN,
    UserRole.CASHIER,
)