from fastapi import APIRouter, Depends, File, UploadFile, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



router = APIRouter()
templates = Jinja2Templates(directory="AR_Copy_Paste/templates")


@router.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,"foo":"bar"})


