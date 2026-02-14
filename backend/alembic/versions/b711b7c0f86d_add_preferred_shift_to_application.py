"""add preferred shift to application

Revision ID: b711b7c0f86d
Revises: a4843ee54200
Create Date: 2026-02-14 08:37:50.791895

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b711b7c0f86d"
down_revision: Union[str, None] = "a4843ee54200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "applications",
        sa.Column(
            "preferred_shift",
            sa.Enum("MORNING", "AFTERNOON", "FLEX", name="workshift_enum"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("applications", "preferred_shift")
