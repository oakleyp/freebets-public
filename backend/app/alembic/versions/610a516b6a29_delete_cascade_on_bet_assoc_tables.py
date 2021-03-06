"""delete cascade on bet assoc tables

Revision ID: 610a516b6a29
Revises: 2e816e363269
Create Date: 2022-06-08 19:55:36.502006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '610a516b6a29'
down_revision = '2e816e363269'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('bets_active_entries_entry_id_fkey', 'bets_active_entries', type_='foreignkey')
    op.drop_constraint('bets_active_entries_bet_id_fkey', 'bets_active_entries', type_='foreignkey')
    op.create_foreign_key(None, 'bets_active_entries', 'bets', ['bet_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'bets_active_entries', 'race_entries', ['entry_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('bets_inactive_entries_bet_id_fkey', 'bets_inactive_entries', type_='foreignkey')
    op.drop_constraint('bets_inactive_entries_entry_id_fkey', 'bets_inactive_entries', type_='foreignkey')
    op.create_foreign_key(None, 'bets_inactive_entries', 'race_entries', ['entry_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'bets_inactive_entries', 'bets', ['bet_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('bets_tags_bet_id_fkey', 'bets_tags', type_='foreignkey')
    op.drop_constraint('bets_tags_tag_id_fkey', 'bets_tags', type_='foreignkey')
    op.create_foreign_key(None, 'bets_tags', 'bets', ['bet_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'bets_tags', 'bet_tags', ['tag_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bets_tags', type_='foreignkey')
    op.drop_constraint(None, 'bets_tags', type_='foreignkey')
    op.create_foreign_key('bets_tags_tag_id_fkey', 'bets_tags', 'bet_tags', ['tag_id'], ['id'])
    op.create_foreign_key('bets_tags_bet_id_fkey', 'bets_tags', 'bets', ['bet_id'], ['id'])
    op.drop_constraint(None, 'bets_inactive_entries', type_='foreignkey')
    op.drop_constraint(None, 'bets_inactive_entries', type_='foreignkey')
    op.create_foreign_key('bets_inactive_entries_entry_id_fkey', 'bets_inactive_entries', 'race_entries', ['entry_id'], ['id'])
    op.create_foreign_key('bets_inactive_entries_bet_id_fkey', 'bets_inactive_entries', 'bets', ['bet_id'], ['id'])
    op.drop_constraint(None, 'bets_active_entries', type_='foreignkey')
    op.drop_constraint(None, 'bets_active_entries', type_='foreignkey')
    op.create_foreign_key('bets_active_entries_bet_id_fkey', 'bets_active_entries', 'bets', ['bet_id'], ['id'])
    op.create_foreign_key('bets_active_entries_entry_id_fkey', 'bets_active_entries', 'race_entries', ['entry_id'], ['id'])
    # ### end Alembic commands ###
