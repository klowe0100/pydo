"""Add config table

Revision ID: 70a828b81ceb
Revises: 747c1748c143
Create Date: 2019-12-13 16:31:36.874304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70a828b81ceb'
down_revision = '747c1748c143'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('config',
    sa.Column('property', sa.String(), nullable=False),
    sa.Column('default', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('user', sa.String(), nullable=True),
    sa.Column('choices', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('property')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('config')
    # ### end Alembic commands ###
