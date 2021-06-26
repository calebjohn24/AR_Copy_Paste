from typing import Optional
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import uvicorn


from AR_Copy_Paste.routers import mobile_api, web_app
app = FastAPI()



app.mount('/static', StaticFiles(directory='./AR_Copy_Paste/static'), name='static')

app.include_router(mobile_api.router)
app.include_router(web_app.router)




if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)