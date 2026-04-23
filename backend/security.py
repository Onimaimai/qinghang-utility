from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 固定的加密密钥（生产环境应该从环境变量获取）
# 使用固定密钥确保重启后仍可解密
_ENCRYPTION_KEY = b'dXRpbGl0eV9wYW5lbF9zZWNyZXRfa2V5XzMyYnl0ZXM='

def get_encryption_key():
    key = os.getenv("ENCRYPTION_KEY")
    if key:
        return key.encode() if isinstance(key, str) else key
    return _ENCRYPTION_KEY


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def encrypt_password(password: str) -> str:
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()
