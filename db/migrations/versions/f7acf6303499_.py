"""empty message

Revision ID: f7acf6303499
Revises: 78b691c1b20e
Create Date: 2019-02-13 07:48:35.372665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7acf6303499'
down_revision = '78b691c1b20e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Element', sa.Column('TagAreaId', sa.Integer(), nullable=True))
    op.create_foreign_key('FK__Area$House$ManagedElementTag', 'Element', 'Area', ['TagAreaId'], ['AreaId'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('FK__Area$House$ManagedElementTag', 'Element', type_='foreignkey')
    op.drop_column('Element', 'TagAreaId')
    # ### end Alembic commands ###
