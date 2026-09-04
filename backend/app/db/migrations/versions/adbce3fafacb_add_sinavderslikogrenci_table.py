"""Add SinavDerslikOgrenci table

Revision ID: adbce3fafacb
Revises: 
Create Date: 2026-09-03 20:04:04.705953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'adbce3fafacb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'SinavDerslikOgrenci',
        sa.Column('SinavID', sa.Integer(), nullable=False),
        sa.Column('DerslikKodu', sa.String(length=20), nullable=False),
        sa.Column('OgrenciNo', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['SinavID'], ['Sinav.SinavID'], ),
        sa.ForeignKeyConstraint(['DerslikKodu'], ['Derslik.DerslikKodu'], ),
        sa.ForeignKeyConstraint(['OgrenciNo'], ['Ogrenci.OgrenciNo'], ),
        sa.PrimaryKeyConstraint('SinavID', 'DerslikKodu', 'OgrenciNo')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('SinavDerslikOgrenci')
