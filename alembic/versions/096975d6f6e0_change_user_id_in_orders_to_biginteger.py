"""Change user_id in orders to BigInteger

Revision ID: 096975d6f6e0
Revises: 8a1c0e53a79c
Create Date: 2025-07-22 09:28:55.780871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '096975d6f6e0'
down_revision: Union[str, Sequence[str], None] = '8a1c0e53a79c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
