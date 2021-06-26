from typing import Optional
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import uvicorn


from AR_Copy_Paste.routers import mobile_api, web_app
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = [
    'http://localhost',
    'http://localhost:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.mount('/static', StaticFiles(directory='./AR_Copy_Paste/static'), name='static')

app.include_router(mobile_api.router)
app.include_router(web_app.router)




if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)