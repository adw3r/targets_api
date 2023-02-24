import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import module.database as _database


class Source(_database.Base):
    __tablename__ = 'sources'

    name = _sql.Column(_sql.String, index=True, primary_key=True)
    lang = _sql.Column(_sql.String, index=True)

    emails = _orm.Relationship('Email', back_populates='source_ref')

    def to_dict(self):
        return {'lang': self.lang}

    def __repr__(self):
        return f'Source(name={self.name}, lang={self.lang})'


class Email(_database.Base):
    __tablename__ = 'emails'

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    email = _sql.Column(_sql.String, index=True)
    source = _sql.Column(_sql.String, _sql.ForeignKey('sources.name'))
    is_available = _sql.Column(_sql.Boolean, default=True, nullable=False)

    source_ref = _orm.Relationship('Source', back_populates='emails')

    def __repr__(self):
        return f'Email(id={self.id}, email={self.email}, source={self.source}, is_available={self.is_available})'
