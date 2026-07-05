"""Add activity_completions table to track awarded activities.

Revision ID: 002_add_activity_completions
Revises: 001_initial
Create Date: 2026-07-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_activity_completions"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

activity_type_enum = sa.Enum(
    "worksheet",
    "quiz",
    "cyp",
    "podcast",
    "video",
    name="activitytype",
)


def upgrade() -> None:
    activity_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "activity_completions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("activity_type", activity_type_enum, nullable=False),
        sa.Column("euros_awarded", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "resource_id", "activity_type", name="uq_activity_completion_user_resource_type"),
    )

    op.create_index("ix_activity_completions_user_id", "activity_completions", ["user_id"], unique=False)
    op.create_index("ix_activity_completions_resource_id", "activity_completions", ["resource_id"], unique=False)
    op.create_index("ix_activity_completions_activity_type", "activity_completions", ["activity_type"], unique=False)
    op.create_index("ix_activity_completions_completed_at", "activity_completions", ["completed_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_activity_completions_completed_at", table_name="activity_completions")
    op.drop_index("ix_activity_completions_activity_type", table_name="activity_completions")
    op.drop_index("ix_activity_completions_resource_id", table_name="activity_completions")
    op.drop_index("ix_activity_completions_user_id", table_name="activity_completions")
    op.drop_table("activity_completions")
    activity_type_enum.drop(op.get_bind(), checkfirst=True)
