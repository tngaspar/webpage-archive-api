from typing import Optional
from fastapi import FastAPI, Form, Request, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from deta import Deta
from datetime import datetime
from utils.url_inspector import validate_url
from utils.archive import archive
from starlette.responses import RedirectResponse
from starlette import status
from utils.user import hash_pw, auth_user, validate_token


# ## secrets file:
from config import deta_private_key


# class Data(BaseModel):
#    username: str = Form()
#    password: str

app = FastAPI(
    title="SaveMyPage API",
    description="An API so save and archive pages for later access",
)
templates = Jinja2Templates(directory="templates")
deta = Deta(deta_private_key)

# creates databases
db = deta.Base("saved_urls")
db_users = deta.Base("users_db")


# read with cookies
@app.get("/", response_class=HTMLResponse)
async def user_get_all_url(request: Request, token: Optional[str] = Cookie(None)):
    if token is None:
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        try:
            username = validate_token(token, db_users)
            # fetches all records from db
            all_user_urls = db.fetch({"username": username})
            return templates.TemplateResponse(
                "index.html", {"request": request, "items": all_user_urls.items}
            )
        except Exception:
            # log not sucessful, token expired
            return templates.TemplateResponse("login.html", {"request": request})


@app.post("/auth", response_class=HTMLResponse)
async def auth(username: str = Form(), password: str = Form()):
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    # get db_user record
    user_in_db = db_users.get(username)
    # auth
    authenticated, user_token = auth_user(username, password, user_in_db)
    if authenticated is True:
        response.set_cookie(key="token", value=user_token)
    return response


# ## User api calls
@app.post("/createUser", response_class=HTMLResponse)
async def createuser(username: str = Form(), password: str = Form()):
    # insert to the database
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    password_hash = hash_pw(password)
    try:
        db_users.insert(
            {
                "key": username,
                "password_hash": password_hash,
                "create_timestamp": datetime.now().timestamp(),
            }
        )
    except Exception:
        # user already exists
        return response
    # auth and redirect
    user_in_db = db_users.get(username)
    # auth
    authenticated, user_token = auth_user(username, password, user_in_db)
    if authenticated is True:
        response.set_cookie(key="token", value=user_token)
    return response


# get all records in db
@app.get("/getall")
async def get_all_url():
    # fetches all records from db
    all_urls = db.fetch()
    return all_urls.items


@app.get("/deleteUI/{key}", response_class=HTMLResponse)
async def deleteUI(request: Request, key: str, token: Optional[str] = Cookie(None)):
    # fetches all records from db
    try:
        validate_token(token, db_users)
        db.delete(key)
    except Exception as ex:
        print(ex)
    return RedirectResponse("/")


@app.post("/saveUI", response_class=HTMLResponse)
async def saveUI(
    request: Request,
    title: str = Form(),
    url: str = Form(),
    token: Optional[str] = Cookie(None),
):
    # check token:
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    try:
        username = validate_token(token, db_users)
        # validate url
        if validate_url(url) is False:
            return response
        # insert to the database
        db.insert(
            {
                "title": title,
                "url": url,
                "timestamp": datetime.now().timestamp(),
                "username": username,
            }
        )
    # not working due to timeout
    # archive(url)
    except Exception as ex:
        print(ex)
    return response


# replace with key
@app.get("/archiveUI/{url:path}", response_class=HTMLResponse)
async def archiveUI(request: Request, url: str):
    # insert to the database
    # not working due to timeout
    archive(url, db)
    return RedirectResponse("/")
