"""added age column

Revision ID: 209e43fad50c
Revises: 
Create Date: 2022-08-03 21:46:15.733136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '209e43fad50c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('age')

    # ### end Alembic commands ###
