from alembic import op
import sqlalchemy as sa

revision = '0002_first_collection'
down_revision = '0001_channels'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('channels', sa.Column('status', sa.String(16), nullable=False, server_default='pending'))
    op.add_column('channels', sa.Column('last_attempt_at', sa.DateTime(timezone=True)))
    op.add_column('channels', sa.Column('last_success_at', sa.DateTime(timezone=True)))
    op.add_column('channels', sa.Column('last_error', sa.Text()))
    op.create_table('posts',
        sa.Column('channel_id', sa.Integer(), sa.ForeignKey('channels.id'), primary_key=True),
        sa.Column('message_id', sa.Integer(), primary_key=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('original_url', sa.Text(), nullable=False),
    )
    op.create_index('ix_posts_published_at', 'posts', ['published_at'])
    op.create_table('channel_observations',
        sa.Column('channel_id', sa.Integer(), sa.ForeignKey('channels.id'), primary_key=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), primary_key=True),
        sa.Column('subscribers', sa.BigInteger()),
    )
    op.create_table('post_observations',
        sa.Column('channel_id', sa.Integer(), primary_key=True),
        sa.Column('message_id', sa.Integer(), primary_key=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), primary_key=True),
        sa.Column('views', sa.BigInteger()),
        sa.Column('reactions', sa.JSON(none_as_null=True)),
        sa.ForeignKeyConstraint(['channel_id', 'message_id'], ['posts.channel_id', 'posts.message_id']),
    )


def downgrade():
    op.drop_table('post_observations')
    op.drop_table('channel_observations')
    op.drop_index('ix_posts_published_at', table_name='posts')
    op.drop_table('posts')
    op.drop_column('channels', 'last_error')
    op.drop_column('channels', 'last_success_at')
    op.drop_column('channels', 'last_attempt_at')
    op.drop_column('channels', 'status')
