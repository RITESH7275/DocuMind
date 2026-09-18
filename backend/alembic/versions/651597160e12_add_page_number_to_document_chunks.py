"""add page number to document chunks

Revision ID: 651597160e12
Revises: 
Create Date: 2026-09-09 00:50:01.916597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '651597160e12'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "document_chunks",
        sa.Column(
            "page_number",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_document_chunks_page_number",
        "document_chunks",
        ["page_number"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_document_chunks_page_number",
        table_name="document_chunks",
    )

    op.drop_column(
        "document_chunks",
        "page_number",
    )