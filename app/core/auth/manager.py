from typing import Optional, TYPE_CHECKING

import logging

from fastapi import Depends, Request, BackgroundTasks
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import BaseUserDatabase

from app.core.auth.dependencies import get_user_db
from app.core.mailing.send_email_confirmation import send_email_confirmation
from app.core.mailing.send_verification_email import send_verification_email
from app.models.user import User
from app.core.settings import settings

if TYPE_CHECKING:
    from fastapi import Request
    from fastapi_users.password import PasswordHelperProtocol


log = logging.getLogger(__name__)


async def get_user_manager(
        background_tasks: BackgroundTasks,
        user_db=Depends(get_user_db),
):
    yield UserManager(user_db, background_tasks=background_tasks)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    def __init__(
            self,
            user_db: BaseUserDatabase[User, int],
            password_helper: Optional["PasswordHelperProtocol"] = None,
            background_tasks: Optional["BackgroundTasks"] = None,
    ):
        super().__init__(user_db, password_helper)
        self.background_tasks = background_tasks

    async def on_after_register(
            self, user: User, request: Optional[Request] = None
    ) -> None:
        log.warning(
            "User %r has registered.",
            user.id
        )

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        log.warning(
            "User %r has forgot their password.",
            user.id
        )

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Verification requested for user {user.id}. Verification token: {token}")

        verification_link = "http://localhost:8000/docs#/auth/verify_verify_auth_verify_post"

        self.background_tasks.add_task(
            send_verification_email,
            user=user,
            verification_link=verification_link,
            verification_token=token,
        )

    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        log.warning(
            "User %r has been verified",
            user.id
        )
        self.background_tasks.add_task(
            send_email_confirmation,
            user=user,
        )