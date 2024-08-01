import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_hard_to_guess_string'
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite://site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    