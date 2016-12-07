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
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String),
        sa.Column('updated', sa.DateTime),
        sa.Column('created', sa.DateTime),
        sa.Column('downloads', sa.Integer),
        sa.Column('description', sa.String),
        sa.Column('repository', sa.String)
    )

def downgrade():
    op.drop_table('packages')
    pass
