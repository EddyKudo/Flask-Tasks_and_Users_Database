"""empty message

Revision ID: 10dbb1a11d40
Revises: a28898131067
Create Date: 2020-03-11 16:56:49.177939

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '10dbb1a11d40'
down_revision = 'a28898131067'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'email',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('user', 'phone',
               existing_type=mysql.VARCHAR(length=15),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'phone',
               existing_type=mysql.VARCHAR(length=15),
               nullable=True)
    op.alter_column('user', 'email',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    # ### end Alembic commands ###
