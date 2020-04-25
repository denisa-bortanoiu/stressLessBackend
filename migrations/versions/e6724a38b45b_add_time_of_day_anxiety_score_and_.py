"""Add time_of_day, anxiety_score and depression_score columns to daily_rating

Revision ID: e6724a38b45b
Revises: f63626251b1b
Create Date: 2020-04-25 12:13:33.773831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6724a38b45b'
down_revision = 'f63626251b1b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('daily_ratings', sa.Column('anxiety_score', sa.Integer(), nullable=True))
    op.add_column('daily_ratings', sa.Column('depression_score', sa.Integer(), nullable=True))
    op.add_column('daily_ratings', sa.Column('time_of_day', sa.Enum('M', 'A', 'E'), nullable=True))


def downgrade():
    op.drop_column('daily_ratings', 'time_of_day')
    op.drop_column('daily_ratings', 'depression_score')
    op.drop_column('daily_ratings', 'anxiety_score')
