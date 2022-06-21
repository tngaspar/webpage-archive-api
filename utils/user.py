from distutils.log import error
import bcrypt
from datetime import datetime, timedelta
from config import db_user_secret_key
import jwt


algorithm = "HS256"


def hash_pw(password):
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    pw_hash = hashed_pw.decode("utf-8")
    return pw_hash


def auth_user(username, password, user_in_db):
    try:
        if bcrypt.checkpw(
            password.encode("utf-8"), user_in_db.get("password_hash").encode("utf-8")
        ):
            access_token_expires = timedelta(minutes=60)
            access_token = _create_access_token(
                data={"username": username}, expires_delta=access_token_expires
            )
            return True, access_token
        else:
            return False, ""
    except Exception:
        return False, ""


def _create_access_token(data, expires_delta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    access_token = jwt.encode(to_encode, db_user_secret_key, algorithm=algorithm)
    return access_token


def _decode_access_token(data):
    token_data = jwt.decode(data, db_user_secret_key, algorithms=algorithm)
    return token_data


def validate_token(token, db_user):
    try:
        payload = _decode_access_token(data=token)
        username = payload.get("username")

        if username is None:
            raise Exception("Authentication Error 1")

    except jwt.PyJWTError:
        raise Exception("Authentication Error 2", token)

    user = db_user.get(username)

    if user is None:
        raise Exception("Authentication Error 3")

    return username
