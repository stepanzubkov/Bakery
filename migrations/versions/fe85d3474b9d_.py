"""empty message

Revision ID: fe85d3474b9d
Revises: 11a1be52a73b
Create Date: 2022-04-05 08:05:41.551998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe85d3474b9d'
down_revision = '11a1be52a73b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'sales',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('products', 'image_url',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'image_url',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('products', 'sales',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###