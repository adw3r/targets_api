import pickle
import logging
from typing import Type

import sqlalchemy.orm as _orm

import module.database as _database
import module.models as _models
import redis
import config

REDIS_CLI = redis.Redis(config.REDIS_HOST)
REDIS_CLI.ping()


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


def get_available_email_from_pool(db: _orm.Session, pool: str) -> Type[_models.Email]:  # fixme
    all_emails: list = get_all_available_emails(db, pool)
    available_email: Type[_models.Email] = all_emails.pop()
    REDIS_CLI.set(f'all_emails_{pool}', pickle.dumps(all_emails))
    return available_email


def get_all_available_emails(db: _orm.Session, pool) -> list:
    all_emails = REDIS_CLI.get(f'all_emails_{pool}')
    if all_emails:
        print('getting cached')
        all_emails = pickle.loads(all_emails)
    else:
        all_emails = get_pool(db, pool, 00)
    print(f'all emails len is {len(all_emails)}')
    REDIS_CLI.set(f'all_emails_{pool}', pickle.dumps(all_emails))
    return all_emails


def get_emails_from_db(db: _orm.Session, pool: str):
    print('getting from sqlite')
    all_emails = db.query(_models.Email).filter_by(source=pool, is_available=True).all()
    all_emails.update({'is_available': False})
    db.commit()
    return all_emails


def get_all_sources_info(db: _orm.Session):
    return_dict = REDIS_CLI.get('return_dict')
    if return_dict:
        return pickle.loads(return_dict)

    sources = db.query(_models.Source).all()
    return_dict = {}
    for source in sources:
        return_dict[source.name] = info(db, source.name)
    REDIS_CLI.set('return_dict', pickle.dumps(return_dict), ex=60*60*1)
    return return_dict


def get_pool(db: _orm.Session, pool: str, limit: int) -> list[Type[_models.Email]]:
    emails = db.query(_models.Email).filter_by(source=pool).limit(limit).all()
    return emails


def info(db: _orm.Session, pool: str):
    source_info: dict = db.query(_models.Source).get(pool).to_dict()
    source_info['amount'] = db.query(_models.Email).filter_by(source=pool).count()
    return source_info
