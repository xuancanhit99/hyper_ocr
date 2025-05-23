"""Add exam time fields to users table

Revision ID: add_exam_time_fields
Revises: a8d5c45116cd
Create Date: 2023-07-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_exam_time_fields'
down_revision: Union[str, None] = 'a8d5c45116cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('time_start', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('duration', sa.Integer(), nullable=True, default=3600))
    op.add_column('users', sa.Column('time_end', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'time_end')
    op.drop_column('users', 'duration')
    op.drop_column('users', 'time_start')
    # ### end Alembic commands ###
