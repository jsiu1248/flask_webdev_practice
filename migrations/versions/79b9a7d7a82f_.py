"""empty message

Revision ID: 79b9a7d7a82f
Revises: ccb39009aad5
Create Date: 2022-10-09 14:56:32.712465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79b9a7d7a82f'
down_revision = 'ccb39009aad5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('compositions', sa.Column('description_html', sa.Text(), nullable=True))
    op.add_column('compositions', sa.Column('slug', sa.String(length=128), nullable=True))
    op.create_unique_constraint(None, 'compositions', ['slug'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'compositions', type_='unique')
    op.drop_column('compositions', 'slug')
    op.drop_column('compositions', 'description_html')
    # ### end Alembic commands ###
