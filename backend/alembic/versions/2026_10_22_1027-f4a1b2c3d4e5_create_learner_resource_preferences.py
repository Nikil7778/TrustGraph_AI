"""create learner resource preferences

Revision ID: f4a1b2c3d4e5
Revises: 2bc971c8c537
Create Date: 2026-10-22 10:27:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'f4a1b2c3d4e5'
down_revision: Union[str, None] = '2bc971c8c537'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()

    # 1. Create user_resource_preferences table if not exists
    if 'user_resource_preferences' not in tables:
        op.create_table(
            'user_resource_preferences',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('primary_platform', sa.String(length=50), nullable=False, server_default='no_preference'),
            sa.Column('preferred_platforms', sa.String(length=255), nullable=False, server_default=''),
            sa.Column('secondary_platforms', sa.String(length=255), nullable=False, server_default=''),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', name='uq_user_resource_preference')
        )
        op.create_index(op.f('ix_user_resource_preferences_id'), 'user_resource_preferences', ['id'], unique=False)
        op.create_index(op.f('ix_user_resource_preferences_user_id'), 'user_resource_preferences', ['user_id'], unique=True)
    else:
        # Table exists - ensure columns preferred_platforms and secondary_platforms exist
        cols = [c['name'] for c in inspector.get_columns('user_resource_preferences')]
        if 'preferred_platforms' not in cols:
            op.add_column('user_resource_preferences', sa.Column('preferred_platforms', sa.String(length=255), nullable=False, server_default=''))
        if 'secondary_platforms' not in cols:
            op.add_column('user_resource_preferences', sa.Column('secondary_platforms', sa.String(length=255), nullable=False, server_default=''))

    # 2. Add description and verified to learning_resources if not exists
    if 'learning_resources' in tables:
        lr_cols = [c['name'] for c in inspector.get_columns('learning_resources')]
        if 'description' not in lr_cols:
            op.add_column('learning_resources', sa.Column('description', sa.String(length=500), nullable=True))
        if 'verified' not in lr_cols:
            op.add_column('learning_resources', sa.Column('verified', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()
    if 'user_resource_preferences' in tables:
        op.drop_table('user_resource_preferences')
