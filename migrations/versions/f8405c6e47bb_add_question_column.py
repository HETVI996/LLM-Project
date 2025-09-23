"""Add question column

Revision ID: f8405c6e47bb
Revises: 
Create Date: 2025-09-23 00:44:01.176396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8405c6e47bb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add column as nullable so existing rows don’t break
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('question', sa.String(length=255), nullable=True))

    # Step 2: Backfill existing rows with default value
    op.execute("UPDATE answer SET question = 'N/A' WHERE question IS NULL")

    # Step 3: Make column NOT NULL after data is filled
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.alter_column('question', nullable=False)

    # Other changes for `answer` table
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.alter_column('answer',
                              existing_type=sa.VARCHAR(length=500),
                              type_=sa.Text(),
                              nullable=False)
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)

    # Other changes for `user` table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('name',
                              existing_type=sa.VARCHAR(length=100),
                              nullable=False)
        batch_op.alter_column('age',
                              existing_type=sa.INTEGER(),
                              nullable=False)
        batch_op.alter_column('gender',
                              existing_type=sa.VARCHAR(length=10),
                              type_=sa.String(length=50),
                              nullable=False)


def downgrade():
    # Revert changes in `user` table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('gender',
                              existing_type=sa.String(length=50),
                              type_=sa.VARCHAR(length=10),
                              nullable=True)
        batch_op.alter_column('age',
                              existing_type=sa.INTEGER(),
                              nullable=True)
        batch_op.alter_column('name',
                              existing_type=sa.VARCHAR(length=100),
                              nullable=True)

    # Revert changes in `answer` table
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)
        batch_op.alter_column('answer',
                              existing_type=sa.Text(),
                              type_=sa.VARCHAR(length=500),
                              nullable=True)
        batch_op.drop_column('question')
