from alembic import op
import sqlalchemy as sa

revision = "0001_channels"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(32), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.UniqueConstraint("username"),
    )


def downgrade():
    op.drop_table("channels")
