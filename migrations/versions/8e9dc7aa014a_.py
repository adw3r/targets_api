"""empty message

Revision ID: 8e9dc7aa014a
Revises: f82377aaae73
Create Date: 2023-06-07 14:21:28.540383

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8e9dc7aa014a'
down_revision = 'f82377aaae73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('api_stats', 'brand',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('api_stats', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('api_stats', 'utm_source',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('api_stats', 'utm_campaign',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('api_stats', 'utm_term',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('api_stats', 'utm_content',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('api_stats', 'utm_medium',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('api_stats', 'promo_code',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('api_stats', 'hits',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('api_stats', 'hosts',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('api_stats', 'registration',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('api_stats', 'new_users',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('api_stats', 'bots',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('api_stats', 'result',
               existing_type=sa.SMALLINT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('api_stats', 'result',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('api_stats', 'bots',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('api_stats', 'new_users',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('api_stats', 'registration',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('api_stats', 'hosts',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('api_stats', 'hits',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('api_stats', 'promo_code',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('api_stats', 'utm_medium',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('api_stats', 'utm_content',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('api_stats', 'utm_term',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('api_stats', 'utm_campaign',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('api_stats', 'utm_source',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('api_stats', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('api_stats', 'brand',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
