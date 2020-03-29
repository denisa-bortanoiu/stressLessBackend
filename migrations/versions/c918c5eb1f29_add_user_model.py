"""Add user model

Revision ID: c918c5eb1f29
Revises: 
Create Date: 2020-03-29 14:13:14.017346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c918c5eb1f29'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255)),
        sa.Column('password', sa.String(255)),
        sa.Column('last_login_time', sa.DateTime, server_default=sa.func.current_timestamp()),
        sa.Column('local_user', sa.Boolean, server_default=sa.false())
    )


def downgrade():
    op.drop_table('users')
