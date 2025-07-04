"""add costo_envio to Orden and product snapshot to OrdenItem

Revision ID: 729dd69b88ed
Revises: 01d4bce9dc97
Create Date: 2025-06-08 16:55:16.220998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '729dd69b88ed'
down_revision: Union[str, None] = '01d4bce9dc97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('orden', sa.Column('costo_envio', sa.Float(), nullable=True))  # Ya existe en la base de datos
    # op.add_column('orden_item', sa.Column('producto_nombre', sa.String(length=100), nullable=True))  # Ya existe en la base de datos
    # op.add_column('orden_item', sa.Column('producto_unidad', sa.String(length=20), nullable=True))  # Ya existe en la base de datos
    # op.alter_column('orden_item', 'producto_id',
    #            existing_type=sa.INTEGER(),
    #            nullable=True)  # Omitido por compatibilidad SQLite y posible estado actual
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orden_item', 'producto_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('orden_item', 'producto_unidad')
    op.drop_column('orden_item', 'producto_nombre')
    op.drop_column('orden', 'costo_envio')
    # ### end Alembic commands ###
