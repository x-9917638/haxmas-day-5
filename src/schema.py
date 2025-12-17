import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.app import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, String, Uuid


def construct_db(app: "Flask"):
    db = SQLAlchemy(app)

    class Message(db.Model):
        __tablename__: str = "messages"

        id: Column[uuid.UUID] = Column(Uuid, primary_key=True)
        text: Column[str] = Column(String(10000), nullable=False, unique=False)
        author: Column[str] = Column(String(64), unique=False)
        password: Column[str] = Column(String(64), nullable=False, unique=False)
        created: Column[datetime] = Column(
            DateTime, default=datetime.now(), unique=False
        )

    db.Message = Message  # pyright: ignore[reportAttributeAccessIssue]

    with app.app_context():
        db.create_all()

    return db
