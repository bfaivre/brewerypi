"""empty message

Revision ID: f252d1ad8d23
Revises: 52534bd6783e
Create Date: 2018-12-18 15:03:17.126879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f252d1ad8d23'
down_revision = '52534bd6783e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Element', sa.Column('IsManaged', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Element', 'IsManaged')
    # ### end Alembic commands ###
