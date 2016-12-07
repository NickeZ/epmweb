"""empty message

Revision ID: bc05ad87d637
Revises: c1b5b91ddd95
Create Date: 2016-12-07 18:53:22.587873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc05ad87d637'
down_revision = 'c1b5b91ddd95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('versions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('packages', sa.Column('max_version', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('packages', 'max_version')
    op.drop_table('versions')
    op.drop_table('users')
    # ### end Alembic commands ###
