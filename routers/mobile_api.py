from fastapi import APIRouter, Depends, File, UploadFile
import uuid
from sqlalchemy.orm import Session
from PIL import Image
from io import BytesIO
from rembg.bg import remove
from pydantic import BaseModel
from AR_Copy_Paste.dependencies import get_db,bucket_name, get_db, s3_bucket
import pytesseract
from AR_Copy_Paste.models.text_model import TextDB

router = APIRouter()

class DeleteText(BaseModel):
    delId:int

class DeleteImg(BaseModel):
    delUrl:str


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
                                               ExpiresIn=3600)
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
        url = s3_bucket.generate_presigned_url(ClientMethod='get_object',
                                               Params={'Bucket': bucket_name,
                                                       'Key': obj['Key']},
                                               ExpiresIn=3600)
        images.append(url)
    
    text = db.query(TextDB).all()
    text = text[::-1]

    return{
        'success':True,
        'images':images,
        'text':text
    }



@router.delete('/api/delete_text')
def delete_text(delete:DeleteText, db: Session = Depends(get_db)):
    del_text = delete.delId
    target_content = db.query(TextDB).filter(TextDB.id == int(del_text)).one()
    db.delete(target_content)
    db.commit()

    return{
        "success":True
    }

@router.delete('/api/delete_img')
def delete_img(delete:DeleteImg):
    del_url = delete.delUrl
    filename_start = del_url.find(bucket_name) + len(bucket_name) + 1
    filename_end = del_url.find(".png") + 4
    del_key = del_url[filename_start:filename_end]
    s3_bucket.delete_object(Bucket=bucket_name,
                                    Key=del_key)


    return{
        "success":True
    }