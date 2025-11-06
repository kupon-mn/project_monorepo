from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", DOUBLE_PRECISION, nullable=False),
        sa.Column(
            "currency", sa.String(length=8), nullable=False, server_default="USD"
        ),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
    )
    op.create_index("ix_products_title", "products", ["title"])


def downgrade() -> None:
    op.drop_index("ix_products_title", table_name="products")
    op.drop_table("products")
