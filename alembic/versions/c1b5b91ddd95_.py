"""empty message

Revision ID: c1b5b91ddd95
Revises: 
Create Date: 2016-12-07 15:09:42.629571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1b5b91ddd95'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'packages',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('downloads', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('repository', sa.String(), nullable=True)
    )

def downgrade():
    op.drop_table('packages')
    pass
