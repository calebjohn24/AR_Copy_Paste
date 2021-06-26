from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from PIL import Image
from io import BytesIO
from rembg.bg import remove
import numpy as np
from AR_Copy_Paste.dependencies import get_db,bucket_name, get_db, s3_bucket
from starlette.responses import StreamingResponse



router = APIRouter()



@router.post('/api/extract_text')
async def extract_text(photo: UploadFile = File(...), db: Session = Depends(get_db)):
    Image.open(BytesIO(await photo.read()))
    file_token = str(uuid.uuid4())
    s3_bucket.put_object(Bucket=bucket_name, Key= file_token +'.jpg',
                                 Body=photo.file,
                                 ACL='private',
            )

    return{
        "success":True
    }

@router.post('/api/extract_object')
async def extract_object(photo: UploadFile = File(...), db: Session = Depends(get_db)):
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