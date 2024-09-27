"""add warehouse

Revision ID: e59f60a248f8
Revises: d1df3f2d78eb
Create Date: 2024-09-28 02:43:07.763616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e59f60a248f8'
down_revision: Union[str, None] = 'd1df3f2d78eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('warehouse',
    sa.Column('warehouse_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('warehouse_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('warehouse')
    # ### end Alembic commands ###