"""empty message

Revision ID: bedfbe2ed80b
Revises: 697bce2315b3
Create Date: 2020-10-30 09:58:42.910341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bedfbe2ed80b'
down_revision = '697bce2315b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('polls', 'places_number')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('polls', sa.Column('places_number', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###