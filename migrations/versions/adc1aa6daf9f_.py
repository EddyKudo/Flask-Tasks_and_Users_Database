"""empty message

Revision ID: adc1aa6daf9f
Revises: c5da428e85a3
Create Date: 2020-02-24 20:05:17.301427

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'adc1aa6daf9f'
down_revision = 'c5da428e85a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todo', 'text',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('user', 'last',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('user', 'name',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'name',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('user', 'last',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('todo', 'text',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    # ### end Alembic commands ###