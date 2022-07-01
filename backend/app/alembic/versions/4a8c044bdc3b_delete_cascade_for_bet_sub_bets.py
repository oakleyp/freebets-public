"""delete cascade for bet-sub_bets

Revision ID: 4a8c044bdc3b
Revises: 610a516b6a29
Create Date: 2022-06-08 21:11:31.315844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a8c044bdc3b'
down_revision = '610a516b6a29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('bets_parent_id_fkey', 'bets', type_='foreignkey')
    op.create_foreign_key(None, 'bets', 'bets', ['parent_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bets', type_='foreignkey')
    op.create_foreign_key('bets_parent_id_fkey', 'bets', 'bets', ['parent_id'], ['id'])
    # ### end Alembic commands ###