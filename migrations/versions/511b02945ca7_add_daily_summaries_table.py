"""Add daily_summaries table

Revision ID: 511b02945ca7
Revises: e6724a38b45b
Create Date: 2020-05-04 18:27:45.012587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '511b02945ca7'
down_revision = 'e6724a38b45b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('daily_summaries',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('steps', sa.Integer(), nullable=True),
        sa.Column('active_minutes', sa.Integer(), nullable=True),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('resting_heart_rate', sa.Integer(), nullable=True),
        sa.Column('sleep_efficiency', sa.Integer(), nullable=True),
        sa.Column('sleep_min_asleep', sa.Integer(), nullable=True),
        sa.Column('sleep_min_in_bed', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('daily_summaries')

