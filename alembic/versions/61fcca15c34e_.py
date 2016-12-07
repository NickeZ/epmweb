"""empty message

Revision ID: 61fcca15c34e
Revises: 
Create Date: 2016-12-07 23:10:04.419158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61fcca15c34e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('packages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('max_version', sa.String(), nullable=False),
    sa.Column('downloads', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('repository', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('versions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('versions')
    op.drop_table('users')
    op.drop_table('packages')
    # ### end Alembic commands ###
