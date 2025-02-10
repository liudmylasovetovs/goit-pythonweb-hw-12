"""fix user role enum

Revision ID: 04ebb516b1cc
Revises: 
Create Date: 2025-02-09 21:23:29.844534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04ebb516b1cc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Створюємо новий тип ENUM вручну
    userrole_enum = sa.Enum('USER', 'ADMIN', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)  # Додаємо перевірку, щоб уникнути дублювання

    # Додаємо колонки
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('role', userrole_enum, nullable=False))



def downgrade() -> None:
    # Спочатку видаляємо колонку
    op.drop_column('users', 'role')
    op.drop_column('users', 'confirmed')

    # Видаляємо тип ENUM
    userrole_enum = sa.Enum('USER', 'ADMIN', name='userrole')
    userrole_enum.drop(op.get_bind(), checkfirst=True)
