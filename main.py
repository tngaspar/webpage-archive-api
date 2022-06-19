from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from deta import Deta
from datetime import datetime
from utils.url_inspector import validate_url
from utils.archive import get_url_archive
from starlette.responses import RedirectResponse

# secrets file:
import config


app = FastAPI(
    title="SaveMyPage API",
    description="An API so save and archive pages for later access",
)
templates = Jinja2Templates(directory="templates")
deta = Deta(config.deta_private_key)

# creates saved_urls database
db = deta.Base("saved_urls")


# call and insert archive
def _archive(url):
    try:
        archive_url = get_url_archive(url)
        url_records = db.fetch({"url": url})
        keys = [item["key"] for item in url_records.items]
        for key in keys:
            db.update({"archive_url": archive_url}, key)
    except Exception as ex:
        print(ex)


# Adds a url to lisk of saved urls
@app.post("/save/{title}/{url:path}")
async def add_url(title: str, url: str):
    # validate url
    if validate_url(url) is False:
        return {"message": "url {url} not in format http(s)://website.com"}
    # insert to the database
    db.insert({"title": title, "url": url,
               "timestamp": datetime.now().timestamp()})
    # not working due to timeout
    # _archive(url)
    # inserts a note with key as id
    print(f"Url inserted: {title} - {url}")
    return {"message": "url successfully added"}


# delete route takes the url id to delete the record from db
@app.delete("/delete/{id}")
async def delete_url(id: str):
    db.delete(id)
    return {"message": f"url with id {id} deleted"}


# get all records in db
@app.get("/getall")
async def get_all_url():
    # fetches all records from db
    all_urls = db.fetch()
    return all_urls.items


# get all records in db
@app.get("/", response_class=HTMLResponse)
async def get_all_url2(request: Request):
    # fetches all records from db
    all_urls = db.fetch()
    return templates.TemplateResponse(
        "index.html", {"request": request, "items": all_urls.items}
    )


@app.get("/deleteUI/{key}", response_class=HTMLResponse)
async def deleteUI(request: Request, key: str):
    # fetches all records from db
    db.delete(key)
    return RedirectResponse("/")


@app.get("/saveUI", response_class=HTMLResponse)
async def saveUI(request: Request, title: str, url: str):
    if validate_url(url) is False:
        return {"message": "url {url} not in format http(s)://website.com"}
    # insert to the database
    db.insert({"title": title, "url": url,
               "timestamp": datetime.now().timestamp()})
    # not working due to timeout
    # _archive(url)
    return RedirectResponse("/")


# replace with key
@app.get("/archiveUI/{url:path}", response_class=HTMLResponse)
async def archiveUI(request: Request, url: str):
    # insert to the database
    # not working due to timeout
    _archive(url)
    return RedirectResponse("/")
