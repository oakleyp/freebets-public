"""Add pool totals to entries, races

Revision ID: c23b5feb3254
Revises: 895e7677d006
Create Date: 2022-07-10 21:38:55.785459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c23b5feb3254'
down_revision = '895e7677d006'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('race', sa.Column('win_pool_total', sa.Float(), nullable=False))
    op.add_column('race', sa.Column('place_pool_total', sa.Float(), nullable=False))
    op.add_column('race', sa.Column('show_pool_total', sa.Float(), nullable=False))
    op.add_column('race_entries', sa.Column('win_pool_total', sa.Float(), nullable=False))
    op.add_column('race_entries', sa.Column('place_pool_total', sa.Float(), nullable=False))
    op.add_column('race_entries', sa.Column('show_pool_total', sa.Float(), nullable=False))
    op.alter_column('race_entries', 'race_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('race_entries', 'race_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('race_entries', 'show_pool_total')
    op.drop_column('race_entries', 'place_pool_total')
    op.drop_column('race_entries', 'win_pool_total')
    op.drop_column('race', 'show_pool_total')
    op.drop_column('race', 'place_pool_total')
    op.drop_column('race', 'win_pool_total')
    # ### end Alembic commands ###