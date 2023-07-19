"""Autoincrement id

Revision ID: 1fa1a103e8b1
Revises: 7ed5b72d745a
Create Date: 2023-07-09 21:42:32.162602

"""
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1fa1a103e8b1"
down_revision = "7ed5b72d745a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user_table", "phone_number", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column("user_table", "id", default=uuid.uuid4, nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user_table", "phone_number", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column("user_table", "id", nullable=False)
    # ### end Alembic commands ###