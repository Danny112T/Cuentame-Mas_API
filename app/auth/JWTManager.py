from jose import jwt
from datetime import datetime
from fastapi import HTTPException, status
from bcrypt import hashpw, gensalt, checkpw
from app.core.config import JWT_SECRET, ALGORITHM

class JWTManager:
    def verify_jwt(token: str):
        try:
            decode_token = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            current_timestamp = datetime.now().timestamp()
            if decode_token is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            elif decode_token["exp"] <= current_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credential's token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return decode_token
        except ValueError:
            return False

    def hashPassword(password: str) -> str:
        passW = password.encode("utf-8")
        return hashpw(passW, gensalt()).decode("utf-8")

    def checkPassword(password: str, hashed: str) -> bool:
        passW = password.encode("utf-8")
        hashed = hashed.encode("utf-8")
        return checkpw(passW, hashed)
