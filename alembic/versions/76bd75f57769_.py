"""Support quest completion tracking

Revision ID: 76bd75f57769
Revises: 97da7b8f3703
Create Date: 2023-01-14 18:50:28.091817

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "76bd75f57769"
down_revision = "97da7b8f3703"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("quest", sa.Column("max_completion_count", sa.Integer(), nullable=True))
    op.add_column(
        "user_quest",
        sa.Column(
            "completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user_quest", "completed")
    op.drop_column("quest", "max_completion_count")
    # ### end Alembic commands ###
