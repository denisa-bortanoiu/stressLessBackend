"""Add minute_series table

Revision ID: 94973117ce43
Revises: 511b02945ca7
Create Date: 2020-05-04 18:45:11.375071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94973117ce43'
down_revision = '511b02945ca7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('minute_series',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('time', sa.String(length=10), nullable=True),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('minute_series')
