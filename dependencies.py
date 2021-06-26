import boto3
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

infoFile = open('./AR_Copy_Paste/private.json')
info = json.load(infoFile)


SQLALCHEMY_DATABASE_URL = info['testDB']

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = info['secretKey']

bucket_session = boto3.session.Session()
s3_bucket = bucket_session.client('s3',
                                      region_name='sfo3',
                                      endpoint_url='https://sfo3.digitaloceanspaces.com',
                                      aws_access_key_id=info['doPublicSpace'],
                                      aws_secret_access_key=info['doSecretSpace'])

bucket_name = 'arcp'


main_link = 'https://e6721e636491.ngrok.io'

