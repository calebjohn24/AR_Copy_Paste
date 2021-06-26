from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from PIL import Image
from io import BytesIO
from rembg.bg import remove
import numpy as np
import pytesseract
from AR_Copy_Paste.dependencies import bucket_name, s3_bucket





router = APIRouter()



@router.post('/api/extract_text')
async def extract_text(photo: UploadFile = File(...)):
    img = Image.open(BytesIO(await photo.read()))
    img_text = pytesseract.image_to_string(img)
    print(img_text)

    pdf = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
    with open('test.pdf', 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default

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