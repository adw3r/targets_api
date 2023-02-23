import asyncio
import logging
from typing import Type

import sqlalchemy.orm as _orm

import module.database as _database
import module.models as _models


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    except Exception as error:
        logging.exception(error)
    finally:
        db.close()


async def get_email_from_pool(db: _orm.Session, pool: str) -> Type[_models.Email]:
    email = None
    while email is None:
        email = db.query(_models.Email).filter_by(is_available=True, source=pool).first()
        if email:
            email.is_available = False
        else:
            all_emails = db.query(_models.Email).filter_by(source=pool, is_available=False)
            all_emails.update({'is_available': True})
    db.commit()
    return email


async def get_pool(db: _orm.Session, pool: str) -> tuple[str]:
    emails = tuple([email.email for email in db.query(_models.Email).filter_by(source=pool).all()])
    return emails


async def info(db: _orm.Session, pool: str):
    source_info: dict = db.query(_models.Source).get(pool).to_dict()
    source_info['available'] = db.query(_models.Email).filter_by(is_available=True, source=pool).count()
    return source_info


async def clear(db: _orm.Session, pool: str):
    all_emails = db.query(_models.Email).filter_by(source=pool)
    all_emails.update({'is_available': False})
    db.commit()


async def reload(db: _orm.Session, pool: str):
    all_emails = db.query(_models.Email).filter_by(source=pool)
    all_emails.update({'is_available': True})
    db.commit()


async def get_all_sources_info(db: _orm.Session):
    sources = db.query(_models.Source).all()
    results = asyncio.gather(*[asyncio.create_task(info(db, source.name)) for source in sources])
    print(results)
    return results
