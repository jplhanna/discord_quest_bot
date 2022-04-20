"""empty message

Revision ID: dd5001604d65
Revises: 60081ae43cc9
Create Date: 2022-04-20 00:46:41.393172

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dd5001604d65"
down_revision = "60081ae43cc9"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("user", "discord_id", existing_type=sa.Integer(), type_=sa.BigInteger())


def downgrade():
    pass
