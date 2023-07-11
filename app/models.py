from datetime import datetime

from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import VARCHAR, SMALLINT, INTEGER, BOOLEAN
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped


class Base(DeclarativeBase):
    ...


class TargetEmail(Base):
    __tablename__ = 'target_emails'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    sent_counter: Mapped[int] = mapped_column(SMALLINT, server_default='default 0', nullable=False)

    source_id: Mapped[int] = mapped_column(SMALLINT, ForeignKey('sources.id'))
    source: Mapped["Source"] = relationship("Source", back_populates='targets', cascade='all')

    def __repr__(self):
        return f'TargetEmail(email = {self.email}, source_id = {self.source_id}, sent = {self.sent_counter})'

    @property
    def dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'source_id': self.source_id,
        }


class Source(Base):
    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(SMALLINT, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, index=True)
    text_id: Mapped[int] = mapped_column(SMALLINT, ForeignKey('texts.id'), index=True)

    is_available: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, server_default='true')

    text: Mapped["Text"] = relationship("Text", back_populates='source')
    targets: Mapped[list["TargetEmail"]] = relationship(
        "TargetEmail", back_populates='source', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'Source(source_name = {self.source_name})'

    @property
    def dict(self):
        return {
            'source_name': self.source_name,
            'lang': self.text.lang,
        }


class SourceInfo(Base):
    __tablename__ = 'sources_info'
    id: Mapped[int] = mapped_column(SMALLINT, primary_key=True)

    source_name: Mapped[str] = mapped_column(VARCHAR(40))
    lang: Mapped[str] = mapped_column(VARCHAR(10))
    amount: Mapped[int] = mapped_column(Integer)


class Text(Base):
    __tablename__ = 'texts'
    id: Mapped[int] = mapped_column(SMALLINT, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String, nullable=False, index=True)
    lang: Mapped[str] = mapped_column(VARCHAR(5), nullable=False, index=True)

    source: Mapped["Source"] = relationship("Source", back_populates='text')


class Referral(Base):
    __tablename__ = 'referrals'
    id: Mapped[int] = mapped_column(SMALLINT, primary_key=True)

    name: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    spins: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    link: Mapped[str] = mapped_column(String, nullable=False)
    available: Mapped[bool] = mapped_column(BOOLEAN, server_default='false')

    def __repr__(self):
        return f'Referral({self.name!r}, {self.spins!r}, {self.link!r}, {self.available!r})'

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'spins': self.spins,
            'link': self.link,
            'available': self.available,
        }


class Bitly(Base):
    __tablename__ = 'bitly_links'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)

    link_id: Mapped[str] = mapped_column(VARCHAR(14), nullable=False)
    long_url: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    link: Mapped[str] = mapped_column(VARCHAR(22), nullable=False)

    def to_dict(self):
        return {
            'link_id': self.link_id,
            'long_url': self.long_url,
            'created_at': self.created_at,
            'link': self.link,
        }


class SpamDonor(Base):
    __tablename__ = 'spam_donors'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    success_count: Mapped[int] = mapped_column(INTEGER, server_default='0')
    fail_count: Mapped[int] = mapped_column(INTEGER, server_default='0')
    status: Mapped[bool] = mapped_column(BOOLEAN, server_default='true')

    donor_name: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, unique=True)
    prom_link: Mapped[str] = mapped_column(VARCHAR(22), nullable=False)
    referral_name: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    targets_source: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)

    def update(self, **kwargs):
        success_count = kwargs.get('success_count')
        if success_count:
            self.success_count = success_count
        status = kwargs.get('status')
        if status:
            self.status = status
        self.donor_name = kwargs['donor_name']
        self.prom_link = kwargs['prom_link']
        self.referral_name = kwargs['referral_name']
        self.targets_source = kwargs['targets_source']

    def dict(self):
        return {
            'id': self.id,
            'donor_name': self.donor_name,
            'success_count': self.success_count,
            'status': self.status,
            'prom_link': self.prom_link,
            'referral_name': self.referral_name,
            'targets_source': self.targets_source
        }


class ApiDataRow(Base):
    __tablename__ = 'api_stats'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)

    brand: Mapped[str] = mapped_column(String, nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    utm_source: Mapped[str] = mapped_column(String, nullable=True)
    utm_campaign: Mapped[str] = mapped_column(String, nullable=True)
    utm_term: Mapped[str] = mapped_column(String, nullable=True)
    utm_content: Mapped[str] = mapped_column(String, nullable=True)
    utm_medium: Mapped[str] = mapped_column(String, nullable=True)
    promo_code: Mapped[str] = mapped_column(String, nullable=True)
    hits: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    hosts: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    registration: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    new_users: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    bots: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    result: Mapped[int] = mapped_column(SMALLINT, nullable=True)

    def __init__(self, **kw):
        kw['date'] = datetime.strptime(kw['date'], '%Y-%m-%d')
        kw['hits'] = int(kw['hits'])
        kw['hosts'] = int(kw['hosts'])
        kw['registration'] = int(kw['registration'])
        kw['new_users'] = int(kw['new_users'])
        kw['bots'] = int(kw['bots'])
        kw['result'] = int(kw['result'])
        super().__init__(**kw)

    def __repr__(self):
        return f'ApiDataRow(utm_source' \
               f'utm_campaign={self.utm_campaign}' \
               f'utm_term={self.utm_term}' \
               f'utm_content={self.utm_content}' \
               f'utm_medium={self.utm_medium}' \
               ')'
