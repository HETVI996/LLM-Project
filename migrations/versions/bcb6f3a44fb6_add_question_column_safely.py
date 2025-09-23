"""add question column safely

Revision ID: bcb6f3a44fb6
Revises: 69da0ccfd51a
Create Date: 2025-09-23 20:08:12.250630
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bcb6f3a44fb6'
down_revision = '69da0ccfd51a'
branch_labels = None
depends_on = None

def upgrade():
    # 1) Add 'question' column as nullable
    op.add_column('answer', sa.Column('question', sa.String(length=255), nullable=True))

    # 2) Fill existing rows with default value
    op.execute("UPDATE answer SET question = 'Unknown' WHERE question IS NULL")

    # 3) Make the column NOT NULL with default
    op.alter_column('answer', 'question',
                    existing_type=sa.String(length=255),
                    nullable=False,
                    server_default=sa.text("'Unknown'"))

def downgrade():
    # Remove the column if downgrading
    op.drop_column('answer', 'question')
