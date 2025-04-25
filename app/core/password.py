from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash_password(password: str) -> str:
    """
    Хеширует пароль для безопасного хранения в базе данных.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Сравнивает пользовательский пароль с хешем из базы данных.
    """
    return pwd_context.verify(plain_password, hashed_password)
