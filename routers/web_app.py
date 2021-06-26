from fastapi import APIRouter, Depends, File, UploadFile, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from AR_Copy_Paste.models.text_model import TextDB
from AR_Copy_Paste.dependencies import get_db,bucket_name, get_db, s3_bucket
from sqlalchemy.orm import Session


router = APIRouter()
templates = Jinja2Templates(directory="AR_Copy_Paste/templates")


@router.get('/', response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    images = []
    text = []
    text_list = []
    text_ids = []

    response = s3_bucket.list_objects(Bucket=bucket_name)
    for obj in response['Contents']:
        url = s3_bucket.generate_presigned_url(ClientMethod='get_object',
                                               Params={'Bucket': bucket_name,
                                                       'Key': obj['Key']},
                                               ExpiresIn=3600)
        images.append(url)
    
    text = db.query(TextDB).all()
    text = text[::-1]
    for t in text:
        text_list.append(t.data)
        text_ids.append(t.id)
    return templates.TemplateResponse("index.html", {"request": request,"text_list":text_list, "text_ids":text_ids, "img_list":images})


