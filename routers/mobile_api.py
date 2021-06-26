from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from PIL import Image
from io import BytesIO
from rembg.bg import remove
import numpy as np
from AR_Copy_Paste.dependencies import get_db,bucket_name, get_db, s3_bucket
import pytesseract
from AR_Copy_Paste.models.text_model import TextDB

router = APIRouter()



@router.post('/api/extract_text')
async def extract_text(photo: UploadFile = File(...), db: Session = Depends(get_db)):
    img = Image.open(BytesIO(await photo.read()))
    img_text = pytesseract.image_to_string(img)
    img_text = img_text.lstrip()
    img_text = img_text.rstrip()
    print(img_text)
    no_space = img_text
    no_space = no_space.replace(" ","")
    no_space = no_space.replace("\f","")
    no_space = no_space.replace("\n","")
    no_space = no_space.replace("\t","")
    if(no_space == ""):
        img_text = "No text Found"
    else:
        print("save db")
        new_content = TextDB(
                data = str(img_text)
            )
        db.add(new_content)
        db.commit()

    return{
        "success":True,
        'img_text':img_text
    }

@router.post('/api/extract_object')
async def extract_object(photo: UploadFile = File(...)):
    result = remove(await photo.read(), alpha_matting=True)
    result_img = Image.open(BytesIO(result)).convert("RGBA")
    result_img.save("tmp.png")
    file_token = str(uuid.uuid4())
    buffer = BytesIO()
    result_img.save(buffer, "PNG")
    buffer.seek(0) # rewind pointer back to start
    s3_bucket.put_object(Bucket=bucket_name, Key= file_token +'.png',
                                 Body=buffer,
                                 ACL='private',
    )

    url = s3_bucket.generate_presigned_url(ClientMethod='get_object',
                                               Params={'Bucket': bucket_name,
                                                       'Key': file_token +'.png'},
                                               ExpiresIn=1200)
    print(url)
    return{
        'success':True,
        'url':url
    }

@router.get('/api/view_data')
def view_data(db: Session = Depends(get_db)):
    images = []
    text = []

    response = s3_bucket.list_objects(Bucket=bucket_name)
    for obj in response['Contents']:
        print(obj['Key'])
        url = s3_bucket.generate_presigned_url(ClientMethod='get_object',
                                               Params={'Bucket': bucket_name,
                                                       'Key': obj['Key']},
                                               ExpiresIn=1200)
        images.append(url)
    
    text = db.query(TextDB).all()
    print(text)

    return{
        'success':True,
        'images':images,
        'text':text
    }



