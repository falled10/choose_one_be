"""empty message

Revision ID: 697bce2315b3
Revises: 8285013310d1
Create Date: 2020-10-23 15:15:47.638827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '697bce2315b3'
down_revision = '8285013310d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('options',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('media', sa.String(), nullable=True),
    sa.Column('poll_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('options')
    # ### end Alembic commands ###