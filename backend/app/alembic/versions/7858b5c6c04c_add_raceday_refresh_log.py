"""Add raceday refresh log

Revision ID: 7858b5c6c04c
Revises: a5deb6a985cb
Create Date: 2022-07-07 16:41:44.570244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7858b5c6c04c'
down_revision = 'a5deb6a985cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('racedayrefreshlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lookahead_start', sa.DateTime(), nullable=False),
    sa.Column('lookahead_end', sa.DateTime(), nullable=False),
    sa.Column('next_check_time', sa.DateTime(), nullable=False),
    sa.Column('race_count', sa.Integer(), nullable=False),
    sa.Column('entry_count', sa.Integer(), nullable=False),
    sa.Column('bet_count', sa.Integer(), nullable=False),
    sa.Column('success', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_racedayrefreshlog_id'), 'racedayrefreshlog', ['id'], unique=False)
    op.create_index(op.f('ix_racedayrefreshlog_lookahead_end'), 'racedayrefreshlog', ['lookahead_end'], unique=False)
    op.create_index(op.f('ix_racedayrefreshlog_lookahead_start'), 'racedayrefreshlog', ['lookahead_start'], unique=False)
    op.create_index(op.f('ix_racedayrefreshlog_next_check_time'), 'racedayrefreshlog', ['next_check_time'], unique=False)
    op.create_index(op.f('ix_racedayrefreshlog_success'), 'racedayrefreshlog', ['success'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_racedayrefreshlog_success'), table_name='racedayrefreshlog')
    op.drop_index(op.f('ix_racedayrefreshlog_next_check_time'), table_name='racedayrefreshlog')
    op.drop_index(op.f('ix_racedayrefreshlog_lookahead_start'), table_name='racedayrefreshlog')
    op.drop_index(op.f('ix_racedayrefreshlog_lookahead_end'), table_name='racedayrefreshlog')
    op.drop_index(op.f('ix_racedayrefreshlog_id'), table_name='racedayrefreshlog')
    op.drop_table('racedayrefreshlog')
    # ### end Alembic commands ###
