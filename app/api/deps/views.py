from fastapi import APIRouter, Depends, HTTPException, status, Header, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, Any
import secrets

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
async def basic_auth_demo_credentials(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    return {"username": credentials.username, "password": credentials.password}


usernames_to_passwords = {
    "user1": "password1",
    "user2": "password2",
    "admin": "admin"
}

static_auth_token_to_username = {
    "adwadWd112e": "admin",
    "afFDF231dfa": "john",
}


def get_auth_user_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    unathed_exc =HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    if credentials.username not in usernames_to_passwords:
        raise unathed_exc

    correct_password = usernames_to_passwords.get(credentials.username)

    if correct_password is None:
        raise unathed_exc
    # secrets

    if not secrets.compare_digest(
            credentials.password.encode("utf-8"),
            correct_password.encode("utf-8")
):
        raise unathed_exc

    return credentials.username


def get_username_by_static_token(
        static_token: str = Header(alias="x-auth-token")
) -> str:
    if token := static_auth_token_to_username.get(static_token):
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing auth token",
    )


@router.get("/basic-auth-username/")
async def basic_auth_demo_checking(
        auth_username: str = Depends(get_auth_user_username)
):
    return {"msg": f"hi! {auth_username}",
            "username": auth_username}


@router.get("/some-http-header-auth/")
async def auth_demo_some_http_header(
        username: str = Depends(get_username_by_static_token)
):
    return {"msg": f"hi! {username}",
            "username": username}


COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


@router.post("/login_cookie/")
async def auth_demo_login_cookie_set(
    response: Response,
    auth_username: str = Depends(get_auth_user_username),
):
    session_id = secrets.token_hex(16)
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok"}

