import os # for environment variables
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://class_ceo:Teamcsc007@team7db.cb26y46s85ai.us-east-2.rds.amazonaws.com:3306/team7DB'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://class_ceo:Teamcsc007@team7db.cb26y46s85ai.us-east-2.rds.amazonaws.com:3306/team7DevDB'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost:3306/team7_local'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


