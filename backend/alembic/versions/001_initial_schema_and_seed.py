"""Initial schema and seed data for Argus LMS.

Revision ID: 001_initial
Revises:
Create Date: 2026-07-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

currency_type_enum = sa.Enum("euros", "house_points", name="currencytype")


def upgrade() -> None:
    op.create_table(
        "houses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("total_points", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_houses_name", "houses", ["name"], unique=False)
    op.create_index("ix_houses_total_points", "houses", ["total_points"], unique=False)

    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("student_count", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="STUDENT", nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=True),
        sa.Column("section_id", sa.Integer(), nullable=True),
        sa.Column("euros_balance", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lifetime_euros", sa.Integer(), server_default="0", nullable=False),
        sa.Column("current_planet", sa.String(length=50), server_default="Mercury", nullable=False),
        sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_active_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("euros_balance >= 0", name="ck_users_euros_balance_non_negative"),
        sa.CheckConstraint("lifetime_euros >= 0", name="ck_users_lifetime_euros_non_negative"),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_euros_balance", "users", ["euros_balance"], unique=False)
    op.create_index("ix_users_last_active_at", "users", ["last_active_at"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=False)

    currency_type_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("currency_type", currency_type_enum, nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"], unique=False)
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"], unique=False)

    houses_table = sa.table(
        "houses",
        sa.column("name", sa.String),
        sa.column("total_points", sa.Integer),
    )
    op.bulk_insert(
        houses_table,
        [
            {"name": "Poseidon", "total_points": 12840},
            {"name": "Mercury", "total_points": 11250},
            {"name": "Apollo", "total_points": 9820},
            {"name": "Zeus", "total_points": 9140},
        ],
    )

    sections_table = sa.table(
        "sections",
        sa.column("name", sa.String),
        sa.column("student_count", sa.Integer),
    )
    op.bulk_insert(
        sections_table,
        [
            {"name": "Grade 12-A", "student_count": 0},
            {"name": "Grade 12-B", "student_count": 0},
            {"name": "Grade 12-C", "student_count": 0},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_index("ix_transactions_created_at", table_name="transactions")
    op.drop_table("transactions")
    currency_type_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_last_active_at", table_name="users")
    op.drop_index("ix_users_euros_balance", table_name="users")
    op.drop_table("users")

    op.drop_table("sections")

    op.drop_index("ix_houses_total_points", table_name="houses")
    op.drop_index("ix_houses_name", table_name="houses")
    op.drop_table("houses")
