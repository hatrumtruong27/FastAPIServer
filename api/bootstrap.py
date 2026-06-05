"""Startup bootstrap helpers for development-safe defaults."""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.app_config import BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_PASSWORD
from api.auth import hash_password
from api.models.db_models import User
from api.repositories.auth_repository import AuthRepository, normalize_email

_logger = logging.getLogger(__name__)


def ensure_bootstrap_admin(db: Session) -> User:
    """Ensure the known development admin login exists on every startup."""
    repo = AuthRepository(db)
    email = normalize_email(BOOTSTRAP_ADMIN_EMAIL)
    password_hash = hash_password(BOOTSTRAP_ADMIN_PASSWORD)
    user = repo.get_user_by_email(email)

    if user is None:
        user = repo.get_first_admin_user()
        if user is None:
            user = User(email=email, password_hash=password_hash, role="admin", is_active=True)
            db.add(user)
        else:
            user.email = email
            user.password_hash = password_hash
            user.role = "admin"
            user.is_active = True
    else:
        user.password_hash = password_hash
        user.role = "admin"
        user.is_active = True

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        user = repo.get_user_by_email(email)
        if user is None:
            raise
        user.password_hash = password_hash
        user.role = "admin"
        user.is_active = True
        db.commit()

    db.refresh(user)
    _logger.info("Bootstrap admin ready: %s", user.email)
    return user
