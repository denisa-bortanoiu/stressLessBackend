"""Add DailyRating model

Revision ID: f63626251b1b
Revises: c918c5eb1f29
Create Date: 2020-03-29 16:46:21.554346

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f63626251b1b'
down_revision = 'c918c5eb1f29'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'daily_ratings',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('general_score', sa.Integer),
        sa.Column('questionnaire_score', sa.Integer),
        sa.Column('day', sa.Date, server_default=sa.func.current_timestamp()),
        sa.Column('user_id', sa.Integer),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                onupdate='CASCADE', ondelete='CASCADE')
    )


def downgrade():
    op.drop_table('daily_ratings')
