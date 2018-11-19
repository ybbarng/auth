from datetime import datetime
import os

from dotenv import load_dotenv
from peewee import *


load_dotenv()
DATABASE_FILENAME = os.getenv('DATABASE_FILENAME')

db = SqliteDatabase(DATABASE_FILENAME)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    created = DateTimeField(default=datetime.utcnow)


class Device(BaseModel):
    user = ForeignKeyField(User, backref='devices')
    name = CharField()
    created = DateTimeField(default=datetime.utcnow)


if __name__ == '__main__':
    with db:
        db.create_tables([User, Device])
