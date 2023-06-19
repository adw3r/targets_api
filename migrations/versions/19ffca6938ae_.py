"""empty message

Revision ID: 19ffca6938ae
Revises: 7f504d3ead10
Create Date: 2023-06-09 14:10:13.599212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19ffca6938ae'
down_revision = '7f504d3ead10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_sources_source_name'), 'sources', ['source_name'], unique=False)
    op.create_index(op.f('ix_texts_id'), 'texts', ['id'], unique=False)
    op.create_index(op.f('ix_texts_lang'), 'texts', ['lang'], unique=False)
    op.create_index(op.f('ix_texts_text'), 'texts', ['text'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_texts_text'), table_name='texts')
    op.drop_index(op.f('ix_texts_lang'), table_name='texts')
    op.drop_index(op.f('ix_texts_id'), table_name='texts')
    op.drop_index(op.f('ix_sources_source_name'), table_name='sources')
    # ### end Alembic commands ###
