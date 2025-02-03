"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-03-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('terrain_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sigma', sa.Float(), nullable=False),
        sa.Column('sea_level', sa.Float(), nullable=False),
        sa.Column('use_power_function', sa.Boolean(), nullable=False),
        sa.Column('continent_factor', sa.Float(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

def downgrade() -> None:
    op.drop_table('terrain_configs') 