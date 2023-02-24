import asyncio
import logging
from typing import Type

import sqlalchemy.orm as _orm

import module.database as _database
import module.models as _models


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db() -> _database.SessionLocal:
    db = _database.SessionLocal()
    try:
        yield db
    except Exception as error:
        logging.exception(error)
    finally:
        db.close()


def get_available_email_from_pool(db: _orm.Session, pool: str) -> Type[_models.Email]:
    available_email = None

    all_emails = db.query(_models.Email).filter_by(source=pool)  # todo cached somehow
    while available_email is None:
        available_email = all_emails.filter_by(is_available=True).first()  # .order_by(_models.Email.is_available.desc())
        if available_email is None:
            all_emails.update({'is_available': True})

    available_email.is_available = False
    db.commit()
    return available_email


def get_all_sources_info(db: _orm.Session) -> dict:
    sources = db.query(_models.Source).all()
    return_dict = {}
    for source in sources:
        return_dict[source.name] = info(db, source.name)
    return return_dict


def get_pool(db: _orm.Session, pool: str, limit: int) -> list[Type[_models.Email]]:
    emails = db.query(_models.Email).filter_by(source=pool).limit(limit).all()
    return emails


def info(db: _orm.Session, pool: str):
    source_info: dict = db.query(_models.Source).get(pool).to_dict()
    source_info['amount'] = db.query(_models.Email).filter_by(source=pool).count()
    return source_info
