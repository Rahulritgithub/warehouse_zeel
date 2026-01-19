"""add transaction_id to items

Revision ID: xxxx_add_transaction_id
Revises: 2dd2583a2c60
Create Date: 2026-01-14
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "xxxx_add_transaction_id"
down_revision: Union[str, Sequence[str], None] = "2dd2583a2c60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1️⃣ Add column
    op.add_column("items", sa.Column("transaction_id", sa.Integer(), nullable=True))

    # 2️⃣ Add foreign key
    op.create_foreign_key(
        "fk_items_transaction_id",
        "items",
        "transactions",
        ["transaction_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_items_transaction_id", "items", type_="foreignkey")
    op.drop_column("items", "transaction_id")
