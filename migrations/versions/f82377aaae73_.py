"""empty message

Revision ID: f82377aaae73
Revises: f9b92f524b14
Create Date: 2023-06-07 14:20:39.357120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f82377aaae73'
down_revision = 'f9b92f524b14'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('api_stats', sa.Column('brand', sa.String(), nullable=False))
    op.add_column('api_stats', sa.Column('date', sa.DateTime(), nullable=False))
    op.add_column('api_stats', sa.Column('utm_source', sa.String(), nullable=False))
    op.add_column('api_stats', sa.Column('utm_campaign', sa.String(), nullable=False))
    op.add_column('api_stats', sa.Column('utm_term', sa.String(), nullable=False))
    op.add_column('api_stats', sa.Column('utm_content', sa.String(), nullable=False))
    op.add_column('api_stats', sa.Column('utm_medium', sa.String(), nullable=False))
    op.add_column('api_stats', sa.Column('promo_code', sa.SMALLINT(), nullable=False))
    op.add_column('api_stats', sa.Column('hits', sa.SMALLINT(), nullable=False))
    op.add_column('api_stats', sa.Column('hosts', sa.SMALLINT(), nullable=False))
    op.add_column('api_stats', sa.Column('registration', sa.SMALLINT(), nullable=False))
    op.add_column('api_stats', sa.Column('new_users', sa.SMALLINT(), nullable=False))
    op.add_column('api_stats', sa.Column('bots', sa.SMALLINT(), nullable=False))
    op.add_column('api_stats', sa.Column('result', sa.SMALLINT(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('api_stats', 'result')
    op.drop_column('api_stats', 'bots')
    op.drop_column('api_stats', 'new_users')
    op.drop_column('api_stats', 'registration')
    op.drop_column('api_stats', 'hosts')
    op.drop_column('api_stats', 'hits')
    op.drop_column('api_stats', 'promo_code')
    op.drop_column('api_stats', 'utm_medium')
    op.drop_column('api_stats', 'utm_content')
    op.drop_column('api_stats', 'utm_term')
    op.drop_column('api_stats', 'utm_campaign')
    op.drop_column('api_stats', 'utm_source')
    op.drop_column('api_stats', 'date')
    op.drop_column('api_stats', 'brand')
    # ### end Alembic commands ###
