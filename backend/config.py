import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Database options
    ALCHEMICAL_DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:port/dbname')

    # Security options
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secretkey')

    # API documentation
    APIFAIRY_TITLE = 'RadioStats API'
    APIFAIRY_VERSION = '1.0.3'
    APIFAIRY_UI = os.environ.get('DOCS_UI', 'elements')
    APIFAIRY_TAGS = ['radios', 'artists', 'songs', 'plays']
