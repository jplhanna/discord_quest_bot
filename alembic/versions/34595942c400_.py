"""empty message

Revision ID: 34595942c400
Revises: eada4e111ff3
Create Date: 2022-09-14 23:50:34.854016

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "34595942c400"
down_revision = "eada4e111ff3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "experience_transaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("datetime_created", sa.DateTime(), nullable=False),
        sa.Column("datetime_edited", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("quest_id", sa.Integer(), nullable=False),
        sa.Column("experience", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["quest_id"],
            ["quest.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("quest", sa.Column("datetime_edited", sa.DateTime(), nullable=True))
    op.add_column("user", sa.Column("datetime_edited", sa.DateTime(), nullable=True))

    op.execute('update "user" set datetime_edited=now();')
    op.execute("update quest set datetime_edited=now();")

    op.alter_column("quest", "datetime_edited", nullable=False)
    op.alter_column("user", "datetime_edited", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "datetime_edited")
    op.drop_column("quest", "datetime_edited")
    op.drop_table("experience_transaction")
    # ### end Alembic commands ###
