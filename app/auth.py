import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr

from app.core import settings, get_logger
from app.db import create_user, get_user_by_email, get_user_by_id

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

HASH_ITERATIONS = 120_000


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    return f"{salt.hex()}:{digest.hex()}"


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        salt_hex, digest_hex = password_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def _create_access_token(payload: Dict[str, Any], expires_minutes: int = 60 * 24 * 7) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    exp = int(time.time()) + expires_minutes * 60
    payload_with_exp = {**payload, "exp": exp}

    header_b64 = _b64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload_with_exp).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256
    ).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def _decode_access_token(token: str) -> Dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(
            settings.secret_key.encode("utf-8"),
            signing_input,
            hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64url_encode(expected_sig), signature_b64):
            raise ValueError("Invalid signature")

        payload_bytes = _b64url_decode(payload_b64)
        payload_str = payload_bytes.decode("utf-8")
        payload = json.loads(payload_str)
        if payload.get("exp", 0) < int(time.time()):
            raise ValueError("Token expired")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def _safe_user(user_row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": user_row["id"],
        "email": user_row["email"],
        "name": user_row.get("name")
    }


@router.post("/register", response_model=AuthResponse)
def register_user(request: RegisterRequest):
    email = request.email.lower().strip()
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = _hash_password(request.password)
    user = create_user(email=email, password_hash=password_hash, name=request.name)
    token = _create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return {"access_token": token, "token_type": "bearer", "user": _safe_user(user)}


@router.post("/login", response_model=AuthResponse)
def login_user(request: LoginRequest):
    email = request.email.lower().strip()
    user = get_user_by_email(email)
    if not user or not _verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return {"access_token": token, "token_type": "bearer", "user": _safe_user(user)}


def get_current_user(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.split(" ", 1)[1]
    payload = _decode_access_token(token)
    user_id = int(payload.get("sub", 0))
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_optional_user(authorization: Optional[str] = Header(default=None)) -> Optional[Dict[str, Any]]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = _decode_access_token(token)
    user_id = int(payload.get("sub", 0))
    return get_user_by_id(user_id)


@router.get("/me")
def who_am_i(user: Dict[str, Any] = Depends(get_current_user)):
    return _safe_user(user)
