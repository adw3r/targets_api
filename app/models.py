from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import VARCHAR, SMALLINT, INTEGER, BOOLEAN
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped


class Base(DeclarativeBase):
    ...


class TargetEmail(Base):
    __tablename__ = 'target_emails'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    sent_counter: Mapped[int] = mapped_column(SMALLINT, nullable=True, index=True, default=0)

    source_id: Mapped[int] = mapped_column(SMALLINT, ForeignKey('sources.id'), index=True)
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
    source_name: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    text_id: Mapped[int] = mapped_column(SMALLINT, ForeignKey('texts.id'), index=True)

    is_available: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    total_sent_counter: Mapped[int] = mapped_column(SMALLINT, default=0, nullable=False)

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


class Text(Base):
    __tablename__ = 'texts'
    id: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    lang: Mapped[str] = mapped_column(VARCHAR(5), nullable=False)

    source: Mapped["Source"] = relationship("Source", back_populates='text')


class Referral(Base):
    __tablename__ = 'referrals'
    id: Mapped[int] = mapped_column(SMALLINT, primary_key=True)

    name: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    spins: Mapped[int] = mapped_column(SMALLINT, nullable=True)
    link: Mapped[str] = mapped_column(String, nullable=False)
    available: Mapped[bool] = mapped_column(BOOLEAN, default=False)

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

    # donor: Mapped[str] = mapped_column(String, nullable=True)
    # targets_source: Mapped[str] = mapped_column(String, nullable=True)
    # referral_name: Mapped[str] = mapped_column(String, nullable=True)

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
    success_count: Mapped[int] = mapped_column(SMALLINT, default=1)
    fail_count: Mapped[int] = mapped_column(SMALLINT, default=0)
    status: Mapped[bool] = mapped_column(BOOLEAN, default=True)

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


class ApiDataRow:
    __tablename__ = 'api_data'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
#
#     brand: Mapped[str] = mapped_column(String)
#     date: Mapped[DateTime] = mapped_column(DateTime)
#     utm_source: Mapped[str] = mapped_column(String)
#     utm_campaign: Mapped[str] = mapped_column(String)
#     utm_term: Mapped[str] = mapped_column(String)
#     utm_content: Mapped[str] = mapped_column(String)
#     utm_medium: Mapped[str] = mapped_column(String)
#     promo_code: Mapped[int] = mapped_column(INT)
#     hits: Mapped[int] = mapped_column(INT)
#     hosts: Mapped[int] = mapped_column(INT)
#     registration: Mapped[int] = mapped_column(INT)
#     new_users: Mapped[int] = mapped_column(INT)
#     bots: Mapped[int] = mapped_column(INT)
#     result: Mapped[int] = mapped_column(INT)
