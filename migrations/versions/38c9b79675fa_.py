"""empty message

Revision ID: 38c9b79675fa
Revises: 6740453c0918
Create Date: 2023-06-21 15:26:25.670685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38c9b79675fa'
down_revision = '6740453c0918'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('target_emails', 'sent_counter',
               existing_type=sa.SMALLINT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('target_emails', 'sent_counter',
               existing_type=sa.SMALLINT(),
               nullable=True)
    # ### end Alembic commands ###
