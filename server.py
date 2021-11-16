import hmac, hashlib, base64
import json

from typing import Optional

from fastapi import FastAPI, Form, Cookie, Body
from fastapi.datastructures import Default
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = "efe212fb12df8cdba0211f1d44a3e45506edef306f5a2188c52d4a9a55f98c77"

PASSWORD_SALT = "9fe5acecf681d3c2e09b048380f80bb25d37669b70e674c61b86f22d2f18f4db"


def sign_data(data: str) -> str:
    """Возвращает подписанные данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()


def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64,sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def verify_password(username: str, password: str) -> bool:
    """Верификация пароля"""
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() ).hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
    return password_hash == stored_password_hash


users = {
    "aidar@user.com": {
        "name": "Aidar",
        "surname": "Dzhumagulov",
        "password": "c75e574b72a59d7d70a5c8cba269093dee07955395167d36945bf934757b59fa",
        "balance": 7777777777
    },
    "ermek@user.com": {
        "name": "Ermek",
        "surname": "Akelov",
        "password": "5a25c4af9cdcbe833dbcd10bc2ad4db2c74a1b679c9c42686400e3ba229a7465",
        "balance": 2222222
    },
    "bogdan@user.com": {
        "name": "Bogdan",
        "surname": "Parshintsev",
        "password": "f23cf57217f80ef36d659e34b9d45c118ba12ed62768474637bb0ca4f9b6402b",
        "balance": 999999999
    },
    "danil@user.com": {
        "name": "Danil",
        "surname": "Emelyanov",
        "password": "5915adbf9ab926be0db30ec6f629a063bd3450d6a5c0a0fec272fcf036d0e776",
        "balance": 88888888
    }
}


@app.get("/")
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
         response = Response(login_page, media_type="text/html")
         response.delete_cookie(key="username")
         return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    return Response(
        f"Hello, {users[valid_username]['name']}<br />"
        f"Your balance is {user['balance']}", 
        media_type="text/html")


@app.post("/login")
def process_login_page(data: dict=Body(...)):
    username = data["username"]
    password = data["password"]
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                'success': False,
                'message': 'I do not know you',
            }),
            media_type='application/json')
    
    response = Response(
        json.dumps({
            'success': True,
            'message': f"Hello dear, {user['name']}. <br />Your balance {user['balance']}"
        }),
        media_type='application/json')

    username_signed = base64.b64encode(username.encode()).decode() + "." + sign_data(username)
    response.set_cookie(key='username', value=username_signed)
    return response
