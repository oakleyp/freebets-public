"""Add sex_restrictions to race

Revision ID: bd3c9a058b0c
Revises: 4a8c044bdc3b
Create Date: 2022-06-17 18:30:41.011175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd3c9a058b0c'
down_revision = '4a8c044bdc3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('race', sa.Column('sex_restrictions', sa.String(), nullable=True))
    op.create_index(op.f('ix_race_sex_restrictions'), 'race', ['sex_restrictions'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_race_sex_restrictions'), table_name='race')
    op.drop_column('race', 'sex_restrictions')
    # ### end Alembic commands ###
