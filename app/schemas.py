from pydantic import BaseModel


class ReferralSchema(BaseModel):
    name: str
    link: str
    available: bool
    spins: int | None = None


class TextSchema(BaseModel):
    text: str
    lang: str


class SpamDonorPostSchema(BaseModel):
    status: bool = True
    fail_count: int = 0
    success_count: int = 0
    donor_name: str
    prom_link: str
    referral_name: str
    targets_source: str


class SpamDonorCount(BaseModel):
    success_count: int = 0
