"""empty message

Revision ID: e5fd3e65f9b9
Revises: eada4e111ff3
Create Date: 2022-12-03 01:26:56.943751

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e5fd3e65f9b9"
down_revision = "eada4e111ff3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("user", "discord_id", existing_type=sa.BIGINT(), nullable=False)
    op.drop_constraint("user_quest_quest_id_fkey", "user_quest", type_="foreignkey")
    op.drop_constraint("user_quest_user_id_fkey", "user_quest", type_="foreignkey")
    op.create_foreign_key(None, "user_quest", "quest", ["quest_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key(None, "user_quest", "user", ["user_id"], ["id"], ondelete="CASCADE")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user_quest", type_="foreignkey")
    op.drop_constraint(None, "user_quest", type_="foreignkey")
    op.create_foreign_key("user_quest_user_id_fkey", "user_quest", "user", ["user_id"], ["id"])
    op.create_foreign_key("user_quest_quest_id_fkey", "user_quest", "quest", ["quest_id"], ["id"])
    op.alter_column("user", "discord_id", existing_type=sa.BIGINT(), nullable=True)
    # ### end Alembic commands ###