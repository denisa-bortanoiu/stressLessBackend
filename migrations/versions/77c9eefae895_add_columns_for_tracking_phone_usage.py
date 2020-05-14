"""Add columns for tracking phone usage

Revision ID: 77c9eefae895
Revises: 94973117ce43
Create Date: 2020-05-14 14:50:23.490822

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77c9eefae895'
down_revision = '94973117ce43'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('minute_series', sa.Column('app_used', sa.String(length=255), nullable=True))
    op.add_column('minute_series', sa.Column('social_media', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('minute_series', 'social_media')
    op.drop_column('minute_series', 'app_used')

