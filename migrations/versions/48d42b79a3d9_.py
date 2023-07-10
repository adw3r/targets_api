"""empty message

Revision ID: 48d42b79a3d9
Revises: 7525780744fd
Create Date: 2023-07-10 12:34:16.309176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48d42b79a3d9'
down_revision = '7525780744fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('spam_donors', 'success_count',
               existing_type=sa.SMALLINT(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text('1'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('spam_donors', 'success_count',
               existing_type=sa.INTEGER(),
               type_=sa.SMALLINT(),
               existing_nullable=False,
               existing_server_default=sa.text('1'))
    # ### end Alembic commands ###
