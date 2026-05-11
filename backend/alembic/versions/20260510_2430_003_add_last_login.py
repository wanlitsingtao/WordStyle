"""添加最后登录时间字段

Revision ID: 20260510_2430_003
Revises: 20260510_2400_002
Create Date: 2026-05-10 24:30:00.000000

说明：为users表添加last_login字段，用于记录用户最后登录时间
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260510_2430_003'
down_revision = '20260510_2400_002'
branch_labels = None
depends_on = None


def upgrade():
    """升级：添加最后登录时间字段"""
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    """降级：删除最后登录时间字段"""
    op.drop_column('users', 'last_login')
